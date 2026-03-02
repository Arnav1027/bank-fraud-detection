"""Pydantic schemas for requests and responses."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============= User Schemas =============
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= Transaction Schemas =============
class TransactionBase(BaseModel):
    """Base transaction schema."""

    amount: float = Field(..., gt=0)
    merchant_id: str
    merchant_category: str
    transaction_location: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Transaction creation schema (for real-time check)."""

    user_id: int
    transaction_timestamp: datetime


class TransactionResponse(TransactionBase):
    """Transaction response schema."""

    id: int
    user_id: int
    fraud_score: float
    is_fraud: bool
    status: str
    model_version: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FraudCheckRequest(BaseModel):
    """Request payload for real-time fraud check."""

    user_id: int
    amount: float = Field(..., gt=0)
    merchant_id: str
    merchant_category: str
    transaction_location: Optional[str] = None
    transaction_timestamp: datetime


class FraudCheckResponse(BaseModel):
    """Response for fraud check endpoint."""

    transaction_id: int
    fraud_score: float
    is_fraud: bool
    risk_level: str  # low, medium, high
    recommendation: str
    explanation: Optional[dict] = None
    processing_time_ms: float


class TransactionListResponse(BaseModel):
    """List of transactions with pagination."""

    total: int
    page: int
    page_size: int
    items: List[TransactionResponse]


# ============= Analytics Schemas =============
class FraudSummary(BaseModel):
    """Summary statistics for fraud analytics."""

    total_transactions: int
    flagged_transactions: int
    fraud_rate: float
    total_amount_at_risk: float
    avg_fraud_score: float
    high_risk_count: int


class FraudAlert(BaseModel):
    """Recent fraud alert."""

    transaction_id: int
    user_id: int
    amount: float
    fraud_score: float
    merchant_id: str
    flagged_at: datetime


class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response."""

    summary: FraudSummary
    top_alerts: List[FraudAlert]
    daily_fraud_counts: dict  # date -> count


class ModelMetricsResponse(BaseModel):
    """Model performance metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    confusion_matrix: dict
    model_version: str
