"""Transaction service for CRUD operations."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from app.models import Transaction, TransactionStatus
from app.schemas import TransactionCreate, TransactionResponse


class TransactionService:
    """Service for transaction operations."""

    @staticmethod
    def create_transaction(
        db: Session,
        transaction_data: Dict[str, Any],
        fraud_score: float,
        is_fraud: bool,
        status: str = TransactionStatus.PROCESSED,
        model_version: str = None,
        raw_features: Dict[str, Any] = None,
    ) -> Transaction:
        """Create a new transaction record."""
        db_transaction = Transaction(
            user_id=transaction_data["user_id"],
            amount=transaction_data["amount"],
            merchant_id=transaction_data["merchant_id"],
            merchant_category=transaction_data["merchant_category"],
            transaction_location=transaction_data.get("transaction_location"),
            transaction_timestamp=transaction_data["transaction_timestamp"],
            fraud_score=fraud_score,
            is_fraud=is_fraud,
            status=status,
            model_version=model_version,
            raw_features=json.dumps(raw_features) if raw_features else None,
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def list_transactions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        is_fraud: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> tuple[List[Transaction], int]:
        """
        List transactions with optional filters.

        Returns:
            Tuple of (transactions list, total count)
        """
        query = db.query(Transaction)

        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)

        if is_fraud is not None:
            query = query.filter(Transaction.is_fraud == is_fraud)

        if start_date:
            query = query.filter(Transaction.transaction_timestamp >= start_date)

        if end_date:
            query = query.filter(Transaction.transaction_timestamp <= end_date)

        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        total = query.count()
        transactions = (
            query.order_by(desc(Transaction.transaction_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return transactions, total

    @staticmethod
    def get_fraud_statistics(
        db: Session,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get fraud statistics for the past N days."""
        start_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(Transaction).filter(
            Transaction.transaction_timestamp >= start_date
        )

        total = query.count()
        flagged = query.filter(Transaction.is_fraud == True).count()
        fraud_rate = flagged / total if total > 0 else 0.0

        # Total amount at risk (flagged transactions)
        amount_at_risk = 0.0
        for txn in query.filter(Transaction.is_fraud == True).all():
            amount_at_risk += txn.amount

        avg_fraud_score = 0.0
        if total > 0:
            from sqlalchemy import func

            result = db.query(func.avg(Transaction.fraud_score)).filter(
                Transaction.transaction_timestamp >= start_date
            ).scalar()
            avg_fraud_score = float(result) if result else 0.0

        # High risk count
        high_risk = query.filter(Transaction.fraud_score >= 0.8).count()

        return {
            "total_transactions": total,
            "flagged_transactions": flagged,
            "fraud_rate": round(fraud_rate, 4),
            "total_amount_at_risk": round(amount_at_risk, 2),
            "avg_fraud_score": round(avg_fraud_score, 4),
            "high_risk_count": high_risk,
        }

    @staticmethod
    def get_daily_fraud_counts(
        db: Session,
        days: int = 30,
    ) -> Dict[str, int]:
        """Get daily fraud counts for the past N days."""
        from sqlalchemy import func

        start_date = datetime.utcnow() - timedelta(days=days)

        results = (
            db.query(
                func.date(Transaction.transaction_timestamp).label("date"),
                func.count(Transaction.id).filter(Transaction.is_fraud == True).label("count"),
            )
            .filter(Transaction.transaction_timestamp >= start_date)
            .group_by(func.date(Transaction.transaction_timestamp))
            .all()
        )

        return {str(date): count for date, count in results}

    @staticmethod
    def get_recent_alerts(
        db: Session,
        limit: int = 10,
        min_fraud_score: float = 0.8,
    ) -> List[Transaction]:
        """Get recent high-risk transactions."""
        return (
            db.query(Transaction)
            .filter(
                Transaction.fraud_score >= min_fraud_score,
            )
            .order_by(desc(Transaction.transaction_timestamp))
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_transaction_status(
        db: Session,
        transaction_id: int,
        status: str,
        notes: Optional[str] = None,
    ) -> Optional[Transaction]:
        """Update transaction status."""
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            transaction.status = status
            if notes:
                transaction.notes = notes
            transaction.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(transaction)
        return transaction
