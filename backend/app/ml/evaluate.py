"""Model evaluation utilities."""

import numpy as np
import pandas as pd
from typing import Dict, Any
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
    roc_curve,
)
import matplotlib.pyplot as plt
import json
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance."""

    @staticmethod
    def evaluate(
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Comprehensive model evaluation.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary with evaluation metrics
        """
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_pred_proba)

        # Precision-Recall AUC
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall_curve, precision_curve)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)

        # ROC curve for plotting
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)

        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "confusion_matrix": {
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp),
            },
            "specificity": float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
            "sensitivity": float(recall),
            "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
            "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
            "class_report": class_report,
        }

        logger.info(f"Evaluation Results:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall: {recall:.4f}")
        logger.info(f"  F1-Score: {f1:.4f}")
        logger.info(f"  ROC-AUC: {roc_auc:.4f}")
        logger.info(f"  PR-AUC: {pr_auc:.4f}")

        # Check constraints
        if recall < 0.95:
            logger.warning(f"Recall {recall:.4f} is below target 0.95")
        if precision < 0.80:
            logger.warning(f"Precision {precision:.4f} is below target 0.80")

        return metrics

    @staticmethod
    def plot_roc_curve(
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        save_path: str = None,
    ) -> None:
        """Plot ROC curve."""
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.2f})")
        plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random Classifier")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend(loc="lower right")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"ROC curve saved to {save_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def plot_precision_recall_curve(
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        save_path: str = None,
    ) -> None:
        """Plot Precision-Recall curve."""
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall_curve, precision_curve)

        plt.figure(figsize=(8, 6))
        plt.plot(
            recall_curve,
            precision_curve,
            color="darkblue",
            lw=2,
            label=f"PR curve (AUC = {pr_auc:.2f})",
        )
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall Curve")
        plt.legend(loc="lower left")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"PR curve saved to {save_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def plot_confusion_matrix(
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        save_path: str = None,
    ) -> None:
        """Plot confusion matrix."""
        from sklearn.metrics import ConfusionMatrixDisplay

        y_pred = model.predict(X_test)

        plt.figure(figsize=(8, 6))
        cm_display = ConfusionMatrixDisplay(
            confusion_matrix=confusion_matrix(y_test, y_pred),
            display_labels=["Legitimate", "Fraud"],
        )
        cm_display.plot()
        plt.title("Confusion Matrix")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()

        plt.close()
