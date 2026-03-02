"""Model training pipeline for fraud detection."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    auc,
    precision_recall_curve,
    confusion_matrix,
    classification_report,
)
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import joblib
import logging

logger = logging.getLogger(__name__)


class FraudModelTrainer:
    """Trainer for fraud detection models."""

    def __init__(self, random_state: int = 42):
        """Initialize trainer."""
        self.random_state = random_state
        self.best_model = None
        self.best_params = None
        self.model_name = None
        self.cv_results = {}
        self.test_metrics = {}

    def train_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        use_smote: bool = True,
    ) -> Dict[str, Any]:
        """
        Train multiple models and select the best one.

        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            use_smote: Whether to apply SMOTE for class imbalance

        Returns:
            Dictionary with results for all models
        """
        results = {}

        # Define models
        models = {
            "LogisticRegression": {
                "model": LogisticRegression(
                    max_iter=1000, random_state=self.random_state, n_jobs=-1
                ),
                "params": {
                    "classifier__C": [0.001, 0.01, 0.1],
                    "classifier__class_weight": ["balanced", None],
                },
            },
            "RandomForest": {
                "model": RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.random_state,
                    n_jobs=-1,
                    max_depth=10,
                ),
                "params": {
                    "classifier__n_estimators": [50, 100],
                    "classifier__max_depth": [8, 10, 12],
                },
            },
            "XGBoost": {
                "model": XGBClassifier(
                    n_estimators=100,
                    random_state=self.random_state,
                    use_label_encoder=False,
                    eval_metric="logloss",
                ),
                "params": {
                    "classifier__max_depth": [3, 5, 7],
                    "classifier__learning_rate": [0.01, 0.1],
                },
            },
        }

        # Build pipeline with SMOTE if needed
        if use_smote:
            pipeline_steps = [
                ("smote", SMOTE(random_state=self.random_state)),
                ("undersampler", RandomUnderSampler(random_state=self.random_state)),
                ("classifier", None),
            ]
        else:
            pipeline_steps = [("classifier", None)]

        best_score = -1
        best_model_name = None

        for model_name, model_config in models.items():
            logger.info(f"Training {model_name}...")

            # Create pipeline
            if use_smote:
                pipeline_steps[-1] = ("classifier", model_config["model"])
                pipeline = Pipeline(pipeline_steps[:-1])
                pipeline.steps.append(("classifier", model_config["model"]))
            else:
                pipeline = model_config["model"]

            # Grid search
            if isinstance(pipeline, Pipeline):
                grid_search = GridSearchCV(
                    pipeline,
                    model_config["params"],
                    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state),
                    scoring="roc_auc",
                    n_jobs=-1,
                    verbose=1,
                )
            else:
                grid_search = GridSearchCV(
                    pipeline,
                    model_config["params"],
                    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state),
                    scoring="roc_auc",
                    n_jobs=-1,
                    verbose=1,
                )

            grid_search.fit(X_train, y_train)

            # Get best estimator
            best_estimator = grid_search.best_estimator_
            if isinstance(best_estimator, Pipeline):
                clf = best_estimator.named_steps["classifier"]
            else:
                clf = best_estimator

            # Evaluate on test set
            y_pred_proba = best_estimator.predict_proba(X_test)[:, 1]
            y_pred = best_estimator.predict(X_test)

            metrics = {
                "best_params": grid_search.best_params_,
                "cv_score": grid_search.best_score_,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
                "roc_auc": roc_auc_score(y_test, y_pred_proba),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            }

            # Calculate PR-AUC
            precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba)
            metrics["pr_auc"] = auc(recall_curve, precision_curve)

            results[model_name] = {
                "model": best_estimator,
                "estimator": clf,
                "metrics": metrics,
            }

            logger.info(f"{model_name} - ROC-AUC: {metrics['roc_auc']:.4f}, Recall: {metrics['recall']:.4f}")

            # Track best model (prioritize recall for fraud detection)
            if metrics["recall"] >= 0.95:
                # If recall meets target, use ROC-AUC as tiebreaker
                score = metrics["roc_auc"]
            else:
                # Otherwise, maximize recall first
                score = metrics["recall"]

            if score > best_score:
                best_score = score
                best_model_name = model_name

        self.best_model = results[best_model_name]["model"]
        self.best_estimator = results[best_model_name]["estimator"]
        self.best_params = results[best_model_name]["metrics"]["best_params"]
        self.model_name = best_model_name
        self.test_metrics = results[best_model_name]["metrics"]

        logger.info(f"Best model: {best_model_name}")

        return results

    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary of test metrics."""
        return self.test_metrics

    def save_model(self, path: str) -> None:
        """Save best model to disk."""
        joblib.dump(self.best_model, path)
        logger.info(f"Model saved to {path}")

    @staticmethod
    def load_model(path: str):
        """Load model from disk."""
        return joblib.load(path)
