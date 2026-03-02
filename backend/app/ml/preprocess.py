"""Data preprocessing and feature engineering for fraud detection."""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
from app.core.config import settings


class FraudPreprocessor:
    """Preprocessing and feature engineering for fraud detection."""

    def __init__(self):
        """Initialize preprocessor with scalers and encoders."""
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: list = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame, target_col: str = "isFraud") -> "FraudPreprocessor":
        """
        Fit the preprocessor on training data.

        Args:
            df: Input dataframe with raw transaction data
            target_col: Name of target column

        Returns:
            self
        """
        # Create a copy to avoid modifying original
        df = df.copy()

        # Engineer features
        df = self._engineer_features(df)

        # Get feature columns (excluding target and id columns)
        feature_cols = [
            col
            for col in df.columns
            if col not in [target_col, "id", "transaction_timestamp"]
        ]

        # Fit label encoders for categorical features
        categorical_cols = df[feature_cols].select_dtypes(
            include=["object"]
        ).columns.tolist()
        for col in categorical_cols:
            le = LabelEncoder()
            le.fit(df[col].fillna("unknown"))
            self.label_encoders[col] = le

        # Encode categorical features
        for col in categorical_cols:
            df[col] = self.label_encoders[col].transform(df[col].fillna("unknown"))

        # Fit scaler on numerical features
        self.scaler.fit(df[feature_cols])
        self.feature_names = feature_cols
        self.is_fitted = True

        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform raw transaction data to feature vectors.

        Args:
            df: Input dataframe with raw transaction data

        Returns:
            Scaled feature array
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        df = df.copy()

        # Engineer features
        df = self._engineer_features(df)

        # Encode categorical features
        for col in self.label_encoders:
            if col in df.columns:
                df[col] = df[col].fillna("unknown")
                # Handle unseen labels by mapping to 0
                encoder = self.label_encoders[col]
                df[col] = df[col].apply(
                    lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
                )

        # Select feature columns
        X = df[self.feature_names]

        # Scale features
        X_scaled = self.scaler.transform(X)

        return X_scaled

    def fit_transform(self, df: pd.DataFrame, target_col: str = "isFraud") -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(df, target_col).transform(df)

    def get_feature_importance_dict(self, importance_scores: np.ndarray) -> Dict[str, float]:
        """Map importance scores to feature names."""
        return {
            name: float(score)
            for name, score in zip(self.feature_names, importance_scores)
        }

    @staticmethod
    def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features from raw transaction data.

        Expected columns: user_id, amount, merchant_category, transaction_timestamp
        Optional columns: transaction_location, merchant_id

        Returns:
            Dataframe with engineered features
        """
        df = df.copy()

        # Time-based features
        if "transaction_timestamp" in df.columns:
            df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"])
            df["hour_of_day"] = df["transaction_timestamp"].dt.hour
            df["day_of_week"] = df["transaction_timestamp"].dt.dayofweek
            df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
            df["month"] = df["transaction_timestamp"].dt.month
        else:
            df["hour_of_day"] = 0
            df["day_of_week"] = 0
            df["is_weekend"] = 0
            df["month"] = 0

        # Amount-based features
        df["log_amount"] = np.log1p(df["amount"])
        df["amount_squared"] = df["amount"] ** 2
        # Handle case where std is 0 or NaN (single row or all same values)
        amount_std = df["amount"].std()
        if pd.isna(amount_std) or amount_std == 0:
            df["amount_normalized"] = 0
        else:
            df["amount_normalized"] = (df["amount"] - df["amount"].mean()) / (amount_std + 1e-8)

        # Merchant category features
        if "merchant_category" in df.columns:
            # Simple risk scoring based on common fraud categories
            high_risk_categories = ["convenience_store", "gas_station", "online"]
            df["merchant_risk_score"] = (
                df["merchant_category"].isin(high_risk_categories)
            ).astype(int)
        else:
            df["merchant_risk_score"] = 0

        # Frequency features (aggregation per user - simplified for real-time)
        if "user_id" in df.columns:
            # In real-time, these would come from DB aggregations
            user_txn_counts = df.groupby("user_id").size()
            df["user_transaction_count"] = df["user_id"].map(user_txn_counts).fillna(1)
        else:
            df["user_transaction_count"] = 1

        # Location feature (presence check)
        if "transaction_location" in df.columns:
            df["has_location"] = (~df["transaction_location"].isna()).astype(int)
        else:
            df["has_location"] = 0

        # Select final feature columns
        feature_cols = [
            "amount",
            "log_amount",
            "amount_squared",
            "amount_normalized",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "month",
            "merchant_risk_score",
            "user_transaction_count",
            "has_location",
        ]

        if "merchant_category" in df.columns:
            feature_cols.append("merchant_category")

        # Keep only available features
        available_cols = [col for col in feature_cols if col in df.columns]

        return df[available_cols + [col for col in df.columns if col not in available_cols]]

    def save(self, path: str) -> None:
        """Save preprocessor to disk."""
        joblib.dump(self, path)

    @staticmethod
    def load(path: str) -> "FraudPreprocessor":
        """Load preprocessor from disk."""
        return joblib.load(path)
