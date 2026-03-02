"""Service for real-time fraud detection."""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any
import joblib
import logging
import time

from app.core.config import settings
from app.ml.preprocess import FraudPreprocessor

logger = logging.getLogger(__name__)


class FraudDetector:
    """Real-time fraud detection service."""

    def __init__(self):
        """Initialize fraud detector with model and preprocessor."""
        self._model = None
        self._preprocessor = None
        self._model_version = "1.0.0"
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load model and preprocessor from disk."""
        try:
            self._model = joblib.load(settings.MODEL_PATH)
            self._preprocessor = joblib.load(settings.PREPROCESSING_PATH)
            logger.info(f"Model loaded from {settings.MODEL_PATH}")
            logger.info(f"Preprocessor loaded from {settings.PREPROCESSING_PATH}")
        except FileNotFoundError:
            logger.warning(
                "Model artifacts not found. Initialize with train_model() before inference."
            )

    def is_ready(self) -> bool:
        """Check if detector is ready for inference."""
        return self._model is not None and self._preprocessor is not None

    def predict(
        self,
        transaction_data: Dict[str, Any],
        threshold: float = None,
    ) -> Dict[str, Any]:
        """
        Predict fraud probability for a transaction.

        Args:
            transaction_data: Dictionary with transaction details:
                - user_id: int
                - amount: float
                - merchant_id: str
                - merchant_category: str
                - transaction_location: Optional[str]
                - transaction_timestamp: datetime

            threshold: Fraud score threshold (default: use config)

        Returns:
            Dictionary with predictions:
                - fraud_score: float (0-1)
                - is_fraud: bool
                - risk_level: str (low/medium/high)
                - processing_time_ms: float
        """
        if not self.is_ready():
            raise RuntimeError("Fraud detector not initialized. Train model first.")

        start_time = time.time()
        threshold = threshold or settings.FRAUD_THRESHOLD

        try:
            # Create dataframe from transaction data
            df = pd.DataFrame([transaction_data])

            # Preprocess and get features
            X = self._preprocessor.transform(df)

            # Get fraud probability
            fraud_proba = self._model.predict_proba(X)[0, 1]
            is_fraud = fraud_proba >= threshold

            # Determine risk level
            if fraud_proba < 0.3:
                risk_level = "low"
            elif fraud_proba < 0.7:
                risk_level = "medium"
            else:
                risk_level = "high"

            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            # Generate explanation
            explanation = self._generate_explanation(X, df, fraud_proba)

            result = {
                "fraud_score": float(fraud_proba),
                "is_fraud": bool(is_fraud),
                "risk_level": risk_level,
                "processing_time_ms": round(processing_time, 2),
                "model_version": self._model_version,
                "threshold_used": threshold,
                "explanation": explanation,
            }

            logger.debug(
                f"Prediction for user {transaction_data.get('user_id')}: "
                f"score={fraud_proba:.4f}, is_fraud={is_fraud}, time={processing_time:.2f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

    def _generate_explanation(
        self,
        X: np.ndarray,
        df: pd.DataFrame,
        fraud_score: float,
    ) -> Dict[str, Any]:
        """
        Generate explanation for fraud prediction.

        Args:
            X: Preprocessed feature array
            df: Original transaction dataframe
            fraud_score: Fraud probability score

        Returns:
            Explanation dictionary with feature contributions
        """
        try:
            feature_names = self._preprocessor.feature_names
            
            # Get feature values
            feature_values = X[0]
            
            # Calculate feature importance using permutation-based approach
            # For tree-based models, use feature importances
            # For linear models, use absolute coefficients
            feature_importance = self._get_feature_importance(feature_values)
            
            # Normalize to percentages
            total_importance = sum(abs(v) for v in feature_importance.values())
            if total_importance > 0:
                feature_percentages = {
                    k: abs(v) / total_importance * 100
                    for k, v in feature_importance.items()
                }
            else:
                feature_percentages = {k: 0 for k in feature_importance}
            
            # Sort by importance
            sorted_features = sorted(
                feature_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top contributing features
            top_features = [
                {
                    "name": feature,
                    "contribution": round(percentage, 1),
                    "value": float(feature_values[feature_names.index(feature)])
                    if feature in feature_names else 0,
                }
                for feature, percentage in sorted_features[:5]
            ]
            
            # Generate insight text
            insights = self._generate_insights(df.iloc[0], top_features, fraud_score)
            
            return {
                "top_features": top_features,
                "confidence": round(self._calculate_confidence(fraud_score) * 100, 1),
                "insights": insights,
                "explanation_text": self._generate_explanation_text(top_features, fraud_score),
            }
        except Exception as e:
            logger.warning(f"Could not generate explanation: {str(e)}")
            return {
                "top_features": [],
                "confidence": 50.0,
                "insights": ["Unable to generate detailed explanation"],
                "explanation_text": "Unable to generate detailed explanation for this prediction",
            }

    def _get_feature_importance(self, feature_values: np.ndarray) -> Dict[str, float]:
        """Get feature importance from model."""
        feature_names = self._preprocessor.feature_names
        
        # For tree-based models (sklearn pipeline)
        if hasattr(self._model, 'named_steps'):
            # Get the final estimator
            final_estimator = self._model.named_steps.get('classifier', self._model[-1])
            if hasattr(final_estimator, 'feature_importances_'):
                importances = final_estimator.feature_importances_
                return {
                    name: importance
                    for name, importance in zip(feature_names, importances)
                }
        
        # Fallback: use absolute feature values as proxy
        return {
            name: abs(value)
            for name, value in zip(feature_names, feature_values)
        }

    def _calculate_confidence(self, fraud_score: float) -> float:
        """Calculate model confidence in the prediction."""
        # Confidence increases as score moves away from 0.5 (threshold)
        return abs(fraud_score - 0.5) * 2 + 0.5

    def _generate_insights(
        self,
        transaction: pd.Series,
        top_features: list,
        fraud_score: float,
    ) -> list:
        """Generate human-readable insights about the prediction."""
        insights = []
        
        # Amount insight
        amount = transaction.get('amount', 0)
        if amount > 1000:
            insights.append(f"High transaction amount (${amount:,.0f}) increases risk")
        
        # Time insight
        if 'transaction_timestamp' in transaction and pd.notna(transaction['transaction_timestamp']):
            try:
                ts = pd.to_datetime(transaction['transaction_timestamp'])
                hour = ts.hour
                if hour >= 22 or hour <= 5:
                    insights.append(f"Unusual transaction time ({hour:02d}:00) raises suspicion")
            except:
                pass
        
        # Category insight
        category = transaction.get('merchant_category', '')
        high_risk_categories = ['jewelry', 'gas_station', 'online', 'casino']
        if any(cat in str(category).lower() for cat in high_risk_categories):
            insights.append(f"Merchant category ({category}) is frequently targeted")
        
        # Score insight
        if fraud_score < 0.3:
            insights.append("Transaction pattern matches legitimate customers")
        elif fraud_score < 0.7:
            insights.append("Multiple risk factors detected - recommend review")
        else:
            insights.append("Strong indicators of fraudulent activity")
        
        return insights if insights else ["Transaction analyzed using ML model"]

    def _generate_explanation_text(self, top_features: list, fraud_score: float) -> str:
        """Generate readable explanation text."""
        if not top_features:
            return "Unable to generate explanation"
        
        features_text = ", ".join([
            f"{f['name']} ({f['contribution']:.1f}%)"
            for f in top_features[:3]
        ])
        
        if fraud_score >= 0.7:
            return f"This transaction is flagged due to: {features_text}. These factors are commonly associated with fraudulent activity."
        elif fraud_score >= 0.3:
            return f"This transaction shows mixed signals: {features_text}. Manual review recommended."
        else:
            return f"This transaction appears legitimate based on: {features_text}."

    def batch_predict(
        self,
        transactions_df: pd.DataFrame,
        threshold: float = None,
    ) -> pd.DataFrame:
        """
        Predict fraud for multiple transactions.

        Args:
            transactions_df: DataFrame with transaction data
            threshold: Fraud score threshold

        Returns:
            DataFrame with original data plus predictions
        """
        if not self.is_ready():
            raise RuntimeError("Fraud detector not initialized. Train model first.")

        threshold = threshold or settings.FRAUD_THRESHOLD

        # Preprocess
        X = self._preprocessor.transform(transactions_df)

        # Predict
        fraud_probas = self._model.predict_proba(X)[:, 1]
        is_fraud = fraud_probas >= threshold

        # Determine risk levels
        risk_levels = np.select(
            [fraud_probas < 0.3, fraud_probas < 0.7],
            ["low", "medium"],
            default="high",
        )

        # Add predictions to dataframe
        result_df = transactions_df.copy()
        result_df["fraud_score"] = fraud_probas
        result_df["is_fraud"] = is_fraud
        result_df["risk_level"] = risk_levels
        result_df["model_version"] = self._model_version

        return result_df

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.is_ready():
            return {"ready": False}

        return {
            "ready": True,
            "model_version": self._model_version,
            "model_type": type(self._model).__name__,
            "threshold": settings.FRAUD_THRESHOLD,
        }

    def update_model(self, model_path: str, preprocessor_path: str) -> None:
        """Update model and preprocessor artifacts."""
        try:
            self._model = joblib.load(model_path)
            self._preprocessor = joblib.load(preprocessor_path)
            logger.info("Model artifacts updated successfully")
        except FileNotFoundError as e:
            logger.error(f"Failed to load artifacts: {str(e)}")
            raise


# Singleton instance
_fraud_detector = None


def get_fraud_detector() -> FraudDetector:
    """Get or create fraud detector instance."""
    global _fraud_detector
    if _fraud_detector is None:
        _fraud_detector = FraudDetector()
    return _fraud_detector
