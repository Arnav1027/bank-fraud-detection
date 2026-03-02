"""Script to train and evaluate fraud detection models."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from faker import Faker
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.preprocess import FraudPreprocessor
from app.ml.train import FraudModelTrainer
from app.ml.evaluate import ModelEvaluator
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_synthetic_data(n_samples: int = 10000, fraud_rate: float = 0.02) -> pd.DataFrame:
    """Generate synthetic transaction data for training."""
    fake = Faker()
    
    logger.info(f"Generating {n_samples} synthetic transactions...")
    
    # Fraud counts
    n_fraud = int(n_samples * fraud_rate)
    n_legit = n_samples - n_fraud
    
    data = []
    merchant_categories = [
        "grocery",
        "gas_station",
        "restaurant",
        "online",
        "entertainment",
        "healthcare",
        "utilities",
        "travel",
    ]
    
    # Generate legitimate transactions
    for i in range(n_legit):
        user_id = fake.random_int(min=1, max=1000)
        amount = fake.random_int(min=10, max=500)
        merchant_category = fake.random_element(merchant_categories)
        location = fake.random_element(["NYC", "LA", "Chicago", "Houston", "Phoenix"])
        timestamp = datetime.utcnow() - timedelta(
            hours=fake.random_int(min=0, max=24 * 30)
        )
        
        data.append({
            "user_id": user_id,
            "amount": amount,
            "merchant_id": f"MERCH_{fake.random_int(min=1, max=5000)}",
            "merchant_category": merchant_category,
            "transaction_location": location,
            "transaction_timestamp": timestamp,
            "isFraud": 0,
        })
    
    # Generate fraudulent transactions (higher amounts, unusual patterns)
    for i in range(n_fraud):
        user_id = fake.random_int(min=1, max=1000)
        amount = fake.random_int(min=500, max=5000)  # Higher amounts for fraud
        merchant_category = fake.random_element(["online", "gas_station", "travel"])
        location = fake.random_element(["NYC", "LA", "Chicago", "Houston", "Phoenix"])
        
        # Add unusual timing
        timestamp = datetime.utcnow() - timedelta(
            hours=fake.random_int(min=22, max=23)
        )
        
        data.append({
            "user_id": user_id,
            "amount": amount,
            "merchant_id": f"MERCH_{fake.random_int(min=4500, max=5000)}",
            "merchant_category": merchant_category,
            "transaction_location": location,
            "transaction_timestamp": timestamp,
            "isFraud": 1,
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Generated {len(df)} transactions: {n_fraud} fraud, {n_legit} legitimate")
    
    return df


def train_and_evaluate():
    """Train and evaluate fraud detection models."""
    logger.info("Starting model training pipeline...")
    
    # Generate data
    df = generate_synthetic_data(n_samples=10000, fraud_rate=0.02)
    
    # Split data
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["isFraud"]
    )
    logger.info(f"Train set: {len(train_df)}, Test set: {len(test_df)}")
    
    # Preprocess
    logger.info("Preprocessing data...")
    preprocessor = FraudPreprocessor()
    X_train = preprocessor.fit_transform(train_df, target_col="isFraud")
    X_test = preprocessor.transform(test_df)
    
    y_train = train_df["isFraud"].values
    y_test = test_df["isFraud"].values
    
    logger.info(f"Features: {preprocessor.feature_names}")
    
    # Train models
    logger.info("Training models...")
    trainer = FraudModelTrainer(random_state=42)
    results = trainer.train_models(X_train, y_train, X_test, y_test, use_smote=True)
    
    # Print results for all models
    logger.info("\n" + "="*60)
    logger.info("MODEL TRAINING RESULTS")
    logger.info("="*60)
    
    for model_name, model_result in results.items():
        metrics = model_result["metrics"]
        logger.info(f"\n{model_name}:")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall: {metrics['recall']:.4f}")
        logger.info(f"  F1-Score: {metrics['f1']:.4f}")
        logger.info(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
        logger.info(f"  PR-AUC: {metrics['pr_auc']:.4f}")
    
    logger.info(f"\nBest Model: {trainer.model_name}")
    logger.info("="*60 + "\n")
    
    # Detailed evaluation of best model
    logger.info("Detailed evaluation of best model...")
    evaluator = ModelEvaluator()
    detailed_metrics = evaluator.evaluate(trainer.best_model, X_test, y_test)
    
    logger.info(f"\nDetailed Metrics:")
    for key, value in detailed_metrics.items():
        if key != "class_report":
            logger.info(f"  {key}: {value}")
    
    # Check constraints
    logger.info("\n" + "="*60)
    logger.info("CONSTRAINT VERIFICATION")
    logger.info("="*60)
    
    recall = detailed_metrics["recall"]
    precision = detailed_metrics["precision"]
    
    logger.info(f"Recall: {recall:.4f} (target: >= 0.95) - {'✓' if recall >= 0.95 else '✗'}")
    logger.info(f"Precision: {precision:.4f} (target: >= 0.80) - {'✓' if precision >= 0.80 else '✗'}")
    logger.info("="*60 + "\n")
    
    # Save artifacts
    logger.info("Saving model and preprocessor artifacts...")
    
    # Create models directory if it doesn't exist
    os.makedirs("app/ml/models", exist_ok=True)
    
    trainer.save_model(settings.MODEL_PATH)
    preprocessor.save(settings.PREPROCESSING_PATH)
    
    logger.info(f"Model saved to {settings.MODEL_PATH}")
    logger.info(f"Preprocessor saved to {settings.PREPROCESSING_PATH}")
    
    # Generate plots
    logger.info("Generating evaluation plots...")
    os.makedirs("plots", exist_ok=True)
    
    ModelEvaluator.plot_roc_curve(trainer.best_model, X_test, y_test, "plots/roc_curve.png")
    ModelEvaluator.plot_precision_recall_curve(
        trainer.best_model, X_test, y_test, "plots/pr_curve.png"
    )
    ModelEvaluator.plot_confusion_matrix(
        trainer.best_model, X_test, y_test, "plots/confusion_matrix.png"
    )
    
    logger.info("Training complete!")
    logger.info("Plots saved to plots/")


if __name__ == "__main__":
    train_and_evaluate()
