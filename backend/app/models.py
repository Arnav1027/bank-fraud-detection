"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst", nullable=False)  # analyst, admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    PROCESSED = "processed"
    FLAGGED = "flagged"


class Transaction(Base):
    """Transaction model with fraud detection results."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    merchant_id = Column(String(100), nullable=False)
    merchant_category = Column(String(100), nullable=False)
    transaction_location = Column(String(255), nullable=True)
    transaction_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Fraud detection results
    fraud_score = Column(Float, nullable=True, default=0.0)
    is_fraud = Column(Boolean, default=False, index=True)
    status = Column(String(50), default=TransactionStatus.PROCESSED, nullable=False)
    
    # Metadata
    raw_features = Column(Text, nullable=True)  # JSON string of features used
    model_version = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
