"""Tests for preprocessing and feature engineering."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.ml.preprocess import FraudPreprocessor


@pytest.fixture
def sample_transactions():
    """Create sample transaction data for testing."""
    data = {
        "user_id": [1, 2, 3, 1, 2, 3],
        "amount": [100.0, 250.0, 50.0, 75.0, 150.0, 200.0],
        "merchant_category": ["grocery", "gas_station", "restaurant", "online", "grocery", "gas_station"],
        "transaction_location": ["NYC", "LA", "NYC", "NYC", "LA", "NYC"],
        "transaction_timestamp": [
            datetime.utcnow() - timedelta(days=i) for i in range(6)
        ],
        "isFraud": [0, 0, 1, 0, 1, 0],
    }
    return pd.DataFrame(data)


def test_preprocessor_fit_transform(sample_transactions):
    """Test preprocessor fit and transform."""
    preprocessor = FraudPreprocessor()
    
    X = preprocessor.fit_transform(sample_transactions)
    
    assert X.shape[0] == len(sample_transactions)
    assert X.shape[1] > 0
    assert preprocessor.is_fitted


def test_preprocessor_feature_engineering(sample_transactions):
    """Test feature engineering."""
    df = FraudPreprocessor._engineer_features(sample_transactions)
    
    # Check for expected engineered features
    expected_features = [
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "month",
        "log_amount",
        "merchant_risk_score",
        "has_location",
    ]
    
    for feature in expected_features:
        assert feature in df.columns


def test_preprocessor_fit_then_transform(sample_transactions):
    """Test fit then transform separately."""
    preprocessor = FraudPreprocessor()
    preprocessor.fit(sample_transactions)
    
    X1 = preprocessor.transform(sample_transactions)
    X2 = preprocessor.transform(sample_transactions)
    
    np.testing.assert_array_almost_equal(X1, X2)


def test_preprocessor_handles_missing_values():
    """Test preprocessor handles missing values."""
    data = {
        "user_id": [1, 2, 3],
        "amount": [100.0, 250.0, 50.0],
        "merchant_category": ["grocery", None, "restaurant"],
        "transaction_location": [None, "LA", "NYC"],
        "transaction_timestamp": [datetime.utcnow()] * 3,
        "isFraud": [0, 1, 0],
    }
    df = pd.DataFrame(data)
    
    preprocessor = FraudPreprocessor()
    X = preprocessor.fit_transform(df)
    
    # Should not raise an error
    assert X.shape[0] == len(df)
    assert not np.isnan(X).any()


def test_preprocessor_saves_and_loads(tmp_path, sample_transactions):
    """Test saving and loading preprocessor."""
    preprocessor = FraudPreprocessor()
    preprocessor.fit(sample_transactions)
    
    # Save
    save_path = tmp_path / "preprocessor.joblib"
    preprocessor.save(str(save_path))
    
    # Load
    loaded_preprocessor = FraudPreprocessor.load(str(save_path))
    
    X1 = preprocessor.transform(sample_transactions)
    X2 = loaded_preprocessor.transform(sample_transactions)
    
    np.testing.assert_array_almost_equal(X1, X2)
