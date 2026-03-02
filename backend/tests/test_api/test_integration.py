"""Integration tests for fraud detection API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import tempfile

from app.main import app
from app.db.session import get_db
from app.models import Base, User, Transaction
from app.core.security import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_user():
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        role="analyst",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Get auth token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_signup():
    """Test user signup."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"


def test_login(test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_password(test_user):
    """Test login with invalid password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_fraud_check_without_auth():
    """Test fraud check endpoint without auth."""
    response = client.post(
        "/api/v1/transactions/check",
        json={
            "user_id": 1,
            "amount": 100.0,
            "merchant_id": "MERCH_001",
            "merchant_category": "grocery",
            "transaction_timestamp": datetime.utcnow().isoformat(),
        },
    )
    assert response.status_code == 403


def test_fraud_check_with_auth(auth_token):
    """Test fraud check endpoint with auth (will fail without model)."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/v1/transactions/check",
        json={
            "user_id": 1,
            "amount": 100.0,
            "merchant_id": "MERCH_001",
            "merchant_category": "grocery",
            "transaction_timestamp": datetime.utcnow().isoformat(),
        },
        headers=headers,
    )
    # Will return 503 because model is not loaded
    assert response.status_code in [200, 503]


def test_list_transactions_without_auth():
    """Test listing transactions without auth."""
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 403


def test_list_transactions_with_auth(auth_token):
    """Test listing transactions with auth."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/transactions/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_summary_without_auth():
    """Test analytics summary without auth."""
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 403


def test_get_summary_with_auth(auth_token):
    """Test analytics summary with auth."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/analytics/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "daily_fraud_counts" in data


def test_list_transactions_with_filters(auth_token):
    """Test listing transactions with filters."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create test transactions
    db = TestingSessionLocal()
    for i in range(5):
        txn = Transaction(
            user_id=1,
            amount=100.0 + i * 10,
            merchant_id=f"MERCH_{i}",
            merchant_category="grocery",
            transaction_timestamp=datetime.utcnow(),
            fraud_score=0.1 * i,
            is_fraud=i > 3,
        )
        db.add(txn)
    db.commit()
    
    # Test filter by amount range
    response = client.get(
        "/api/v1/transactions/?min_amount=110&max_amount=130",
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
