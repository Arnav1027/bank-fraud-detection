"""Transaction routes for fraud detection."""

from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import pandas as pd
import io
import csv

from app.db.session import get_db
from app.models import User, Transaction
from app.schemas import (
    FraudCheckRequest,
    FraudCheckResponse,
    TransactionResponse,
    TransactionListResponse,
)
from app.api.dependencies import get_current_user
from app.services.fraud_detector import get_fraud_detector
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/check", response_model=FraudCheckResponse)
def check_fraud(
    request: FraudCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a transaction for real-time fraud scoring.

    Returns fraud probability and risk classification.
    """
    detector = get_fraud_detector()

    if not detector.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detector model not loaded",
        )

    # Prepare transaction data
    transaction_data = {
        "user_id": request.user_id,
        "amount": request.amount,
        "merchant_id": request.merchant_id,
        "merchant_category": request.merchant_category,
        "transaction_location": request.transaction_location,
        "transaction_timestamp": request.transaction_timestamp,
    }

    # Get fraud prediction
    prediction = detector.predict(transaction_data)

    # Store transaction in database
    db_transaction = TransactionService.create_transaction(
        db=db,
        transaction_data=transaction_data,
        fraud_score=prediction["fraud_score"],
        is_fraud=prediction["is_fraud"],
        model_version=prediction["model_version"],
    )

    # Determine recommendation
    recommendation = "APPROVE"
    if prediction["is_fraud"]:
        recommendation = "BLOCK"
    elif prediction["risk_level"] == "medium":
        recommendation = "REVIEW"

    return FraudCheckResponse(
        transaction_id=db_transaction.id,
        fraud_score=prediction["fraud_score"],
        is_fraud=prediction["is_fraud"],
        risk_level=prediction["risk_level"],
        recommendation=recommendation,
        explanation=prediction.get("explanation"),
        processing_time_ms=prediction["processing_time_ms"],
    )


@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    is_fraud: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List transactions with optional filters.

    Supported filters:
    - user_id: Filter by user
    - is_fraud: Filter by fraud status
    - start_date, end_date: Filter by timestamp range
    - min_amount, max_amount: Filter by amount range
    """
    transactions, total = TransactionService.list_transactions(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        is_fraud=is_fraud,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    return TransactionListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=[TransactionResponse.model_validate(t) for t in transactions],
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transaction details by ID."""
    transaction = TransactionService.get_transaction(db, transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return TransactionResponse.model_validate(transaction)


@router.post("/batch")
def batch_check_fraud(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file for batch fraud analysis.

    Expected columns: user_id, amount, merchant_id, merchant_category,
                     transaction_location, transaction_timestamp

    Returns a CSV with fraud scores appended.
    """
    detector = get_fraud_detector()

    if not detector.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud detector model not loaded",
        )

    try:
        # Read CSV file
        contents = file.file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Validate required columns
        required_cols = [
            "user_id",
            "amount",
            "merchant_id",
            "merchant_category",
            "transaction_timestamp",
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_cols)}",
            )

        # Convert timestamp column
        df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"])

        # Get batch predictions
        results_df = detector.batch_predict(df)

        # Store all transactions in database
        for _, row in results_df.iterrows():
            TransactionService.create_transaction(
                db=db,
                transaction_data={
                    "user_id": int(row["user_id"]),
                    "amount": float(row["amount"]),
                    "merchant_id": str(row["merchant_id"]),
                    "merchant_category": str(row["merchant_category"]),
                    "transaction_location": row.get("transaction_location"),
                    "transaction_timestamp": row["transaction_timestamp"],
                },
                fraud_score=float(row["fraud_score"]),
                is_fraud=bool(row["is_fraud"]),
                model_version=row["model_version"],
            )

        # Create CSV response
        output = io.StringIO()
        results_df.to_csv(output, index=False)

        return {
            "status": "success",
            "records_processed": len(results_df),
            "fraud_count": int(results_df["is_fraud"].sum()),
            "csv_data": output.getvalue(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}",
        )
