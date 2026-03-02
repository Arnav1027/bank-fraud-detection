"""Analytics routes for dashboard data."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models import User
from app.schemas import AnalyticsSummaryResponse, FraudSummary, FraudAlert
from app.api.dependencies import get_current_user
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_summary(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get fraud statistics summary.

    - days: Number of days to analyze (default: 7)
    """
    # Get fraud statistics
    stats = TransactionService.get_fraud_statistics(db, days=days)

    fraud_summary = FraudSummary(
        total_transactions=stats["total_transactions"],
        flagged_transactions=stats["flagged_transactions"],
        fraud_rate=stats["fraud_rate"],
        total_amount_at_risk=stats["total_amount_at_risk"],
        avg_fraud_score=stats["avg_fraud_score"],
        high_risk_count=stats["high_risk_count"],
    )

    # Get recent alerts
    alerts = TransactionService.get_recent_alerts(db, limit=10, min_fraud_score=0.8)
    top_alerts = [
        FraudAlert(
            transaction_id=alert.id,
            user_id=alert.user_id,
            amount=alert.amount,
            fraud_score=alert.fraud_score,
            merchant_id=alert.merchant_id,
            flagged_at=alert.transaction_timestamp,
        )
        for alert in alerts
    ]

    # Get daily fraud counts
    daily_counts = TransactionService.get_daily_fraud_counts(db, days=days)

    return AnalyticsSummaryResponse(
        summary=fraud_summary,
        top_alerts=top_alerts,
        daily_fraud_counts=daily_counts,
    )


@router.get("/alerts")
def get_alerts(
    limit: int = Query(20, ge=1, le=100),
    min_fraud_score: float = Query(0.8, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get recent high-risk transaction alerts.

    - limit: Maximum number of alerts to return
    - min_fraud_score: Minimum fraud score threshold for alerting
    """
    alerts = TransactionService.get_recent_alerts(
        db, limit=limit, min_fraud_score=min_fraud_score
    )

    return {
        "alerts": [
            {
                "transaction_id": alert.id,
                "user_id": alert.user_id,
                "amount": alert.amount,
                "fraud_score": alert.fraud_score,
                "merchant_id": alert.merchant_id,
                "merchant_category": alert.merchant_category,
                "flagged_at": alert.transaction_timestamp,
                "location": alert.transaction_location,
            }
            for alert in alerts
        ],
        "count": len(alerts),
    }


@router.get("/metrics")
def get_metrics(
    current_user: User = Depends(get_current_user),
):
    """Get model performance metrics (placeholder for trained model)."""
    # These would be loaded from model evaluation results
    return {
        "accuracy": 0.95,
        "precision": 0.85,
        "recall": 0.98,
        "f1_score": 0.91,
        "roc_auc": 0.96,
        "pr_auc": 0.88,
        "confusion_matrix": {
            "true_negatives": 9500,
            "false_positives": 300,
            "false_negatives": 10,
            "true_positives": 490,
        },
        "model_version": "1.0.0",
    }
