# Machine Learning Pipeline Documentation

## Overview

The fraud detection ML pipeline is designed to identify fraudulent banking transactions with high recall (≥95%) while maintaining reasonable precision (≥80%). The system uses multiple algorithms and advanced techniques to handle class imbalance typical in fraud datasets.

---

## Data Pipeline

### 1. Data Sources

The system supports:
- **Real-time transactions**: Single transaction input via API
- **Batch processing**: CSV file uploads
- **Training data**: Synthetic data generation for demo (Faker library)
- **Production data**: PostgreSQL database

### 2. Dataset Characteristics

```
Typical Distribution:
├─ Legitimate: ~98%
└─ Fraudulent: ~2%

Features: 11+ engineered features
Samples: 10,000+ recommended for training
Time Period: Last 30-90 days recommended
```

---

## Feature Engineering

### Raw Features (Input)

Required:
- `user_id`: Unique user identifier
- `amount`: Transaction amount (numerical)
- `merchant_id`: Merchant identifier
- `merchant_category`: Category (e.g., grocery, gas_station)
- `transaction_timestamp`: Transaction date/time

Optional:
- `transaction_location`: Geographic location

### Engineered Features

#### Time-Based (4 features)
```python
hour_of_day = transaction_timestamp.hour  # 0-23
day_of_week = transaction_timestamp.dayofweek  # 0-6
is_weekend = (day_of_week >= 5).astype(int)  # 0/1
month = transaction_timestamp.month  # 1-12
```

#### Amount-Based (4 features)
```python
log_amount = log(amount + 1)  # Log scale
amount_squared = amount ** 2  # Non-linear
amount_normalized = (amount - mean) / std  # Standardized
```

#### Merchant Features (2 features)
```python
merchant_risk_score = category in high_risk_categories  # 0/1
merchant_category_encoded = LabelEncoder(category)
```

#### User Features (1+ features)
```python
user_transaction_count = txns per user
```

#### Location Features (1 feature)
```python
has_location = 1 if location else 0
```

### Feature Statistics

```python
# After preprocessing on training data:
Total Features: 11-13 (depending on categorical encoding)
Numerical: 10
Categorical: 1-3
Missing Values: Handled with forward fill or default values
Scaling: StandardScaler applied to all features
```

---

## Preprocessing Pipeline

### Steps

```python
from app.ml.preprocess import FraudPreprocessor

preprocessor = FraudPreprocessor()

# Fit on training data (calculates statistics)
preprocessor.fit(training_df, target_col='isFraud')

# Transform new data (applies learned statistics)
X_train = preprocessor.transform(training_df)
X_test = preprocessor.transform(test_df)
```

### Workflow

```
Raw Data
  ↓
Feature Engineering (create new features)
  ↓
Label Encoding (categorical → numerical)
  ↓
Standardization (mean=0, std=1)
  ↓
Ready for Model
```

### Handled Cases

- Missing values: Filled with 'unknown' for categorical
- Outliers: Handled by StandardScaler
- Categorical variables: LabelEncoder applied
- Feature scaling: StandardScaler for all numerical features

---

## Model Selection & Training

### Models Trained

#### 1. **Logistic Regression** (Baseline)

```python
LogisticRegression(
    max_iter=1000,
    class_weight='balanced',  # Handle class imbalance
    penalty='l2'
)
```

**Pros:**
- Fast, interpretable, baseline
- Good probability calibration
- Efficient at inference

**Cons:**
- Assumes linear decision boundary
- May underfit on complex patterns

**Hyperparameters Tuned:**
- C: [0.001, 0.01, 0.1]
- class_weight: ['balanced', None]

#### 2. **Random Forest** (Ensemble)

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=[8, 10, 12],
    n_jobs=-1,
    random_state=42
)
```

**Pros:**
- Captures non-linear patterns
- Feature importance ranking
- Robust to outliers
- Parallelizable

**Cons:**
- Less interpretable
- Requires more memory
- Can overfit on small datasets

**Hyperparameters Tuned:**
- n_estimators: [50, 100]
- max_depth: [8, 10, 12]

#### 3. **XGBoost** (Gradient Boosting)

```python
XGBClassifier(
    n_estimators=100,
    max_depth=[3, 5, 7],
    learning_rate=[0.01, 0.1],
    objective='binary:logistic',
    eval_metric='logloss',
    use_label_encoder=False
)
```

**Pros:**
- State-of-the-art performance
- Fast training and inference
- Built-in feature importance
- Handles class imbalance well

**Cons:**
- More hyperparameters to tune
- Can overfit if not carefully tuned

**Hyperparameters Tuned:**
- max_depth: [3, 5, 7]
- learning_rate: [0.01, 0.1]

---

## Class Imbalance Handling

### Problem

Fraud datasets are extremely imbalanced:
- Fraud: ~2% of transactions
- Legitimate: ~98% of transactions

This causes models to:
- Bias toward majority class
- Fail to learn fraud patterns
- Give poor probability calibration

### Solution: Hybrid Approach

```python
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

pipeline = Pipeline([
    ('smote', SMOTE(sampling_strategy=0.5, random_state=42)),
    ('undersampler', RandomUnderSampler(sampling_strategy=0.7, random_state=42)),
    ('classifier', XGBClassifier())
])
```

### Techniques

#### 1. SMOTE (Oversampling)
- Synthetic Minority Oversampling Technique
- Creates synthetic samples in feature space
- Reduces variance, increases bias (controlled)

#### 2. Random Undersampling
- Removes majority class samples randomly
- Reduces dataset size, retains information
- Prevents overfitting to majority

#### 3. Class Weighting (in models)
- Some models support `class_weight='balanced'`
- Penalizes misclassification of minority class
- Works well with Logistic Regression, XGBoost

### Sampling Strategy

```
Original:  98% legitimate, 2% fraud
After SMOTE (0.5): 67% legitimate, 33% fraud
After Undersampling (0.7): 30% legitimate, 70% fraud
```

---

## Model Training & Hyperparameter Tuning

### Cross-Validation Strategy

```python
stratified_kfold = StratifiedKFold(
    n_splits=5,  # 5-fold cross-validation
    shuffle=True,
    random_state=42
)

grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grids,
    cv=stratified_kfold,
    scoring='roc_auc',  # Optimal for imbalanced data
    n_jobs=-1
)
```

**Why Stratified K-Fold:**
- Maintains fraud/legitimate ratio in each fold
- More representative than random split
- Better for imbalanced data

**Why ROC-AUC:**
- Threshold-independent metric
- Works well with imbalanced data
- Focuses on model discrimination

### Training Process

```
Step 1: Load and explore data
Step 2: Split train/test (stratified, 80/20)
Step 3: Apply preprocessing (fit on train)
Step 4: For each model:
        - Create pipeline with SMOTE/undersampling
        - GridSearchCV with stratified 5-fold
        - Train on full training set with best params
Step 5: Evaluate on test set
Step 6: Select best model (highest recall ≥ 0.95)
Step 7: Save model and preprocessor artifacts
```

### Hyperparameter Selection

Grid sizes are intentionally limited to:
- Keep training time reasonable (~5-10 minutes)
- Prevent overfitting with too many options
- Balance exploration vs exploitation

```python
# Example from XGBoost grid
'max_depth': [3, 5, 7],  # 3 options
'learning_rate': [0.01, 0.1]  # 2 options
# Total combinations: 3 × 2 = 6 per fold × 5 folds
```

---

## Model Evaluation

### Metrics Computed

```
1. Classification Metrics
   ├─ Accuracy: (TP + TN) / Total
   ├─ Precision: TP / (TP + FP)  [focus: minimize false alerts]
   ├─ Recall: TP / (TP + FN)  [focus: catch fraud]
   ├─ F1-Score: 2 × (Precision × Recall) / (Precision + Recall)
   ├─ Specificity: TN / (TN + FP)
   └─ False Positive Rate: FP / (FP + TN)

2. Ranking Metrics (Threshold-independent)
   ├─ ROC-AUC: Area under ROC curve
   └─ PR-AUC: Area under Precision-Recall curve

3. Confusion Matrix
   ├─ True Positives (TP): Correctly identified fraud
   ├─ True Negatives (TN): Correctly identified legitimate
   ├─ False Positives (FP): Legitimate flagged as fraud
   └─ False Negatives (FN): Fraud missed
```

### Performance Targets

```python
targets = {
    'recall': >= 0.95,         # Catch 95%+ of fraud
    'precision': >= 0.80,      # 80%+ of alerts are real fraud
    'f1_score': >= 0.88,       # Balanced metric
    'roc_auc': >= 0.95,        # Excellent discrimination
    'pr_auc': >= 0.85          # Good on imbalanced data
}
```

### Confusion Matrix Interpretation

```
                  Predicted
              Fraud    Legitimate
Actual Fraud   TP          FN
      Legit    FP          TN

For fraud detection:
- FN is BAD (missed fraud) → Want LOW FN (HIGH recall)
- FP is OK (false alert) → Acceptable if precision > 80%
```

### Evaluation Plots

```
1. ROC Curve
   - X: False Positive Rate (1 - Specificity)
   - Y: True Positive Rate (Recall)
   - Diagonal: Random classifier (AUC=0.5)
   - Goal: Curve close to top-left (high TPR, low FPR)

2. Precision-Recall Curve
   - X: Recall (TPR)
   - Y: Precision
   - Better for imbalanced data than ROC
   - Goal: Curve close to top-right

3. Confusion Matrix Heatmap
   - Shows TP, TN, FP, FN distribution
   - Easy visual assessment
```

---

## Inference & Scoring

### Real-Time Prediction

```python
from app.services.fraud_detector import get_fraud_detector

detector = get_fraud_detector()

# Single transaction
result = detector.predict({
    'user_id': 1,
    'amount': 150.0,
    'merchant_id': 'M001',
    'merchant_category': 'grocery',
    'transaction_location': 'NYC',
    'transaction_timestamp': datetime.now()
})

# Returns:
{
    'fraud_score': 0.12,        # 0-1, higher = more fraud-like
    'is_fraud': False,          # score >= threshold
    'risk_level': 'low',        # low/medium/high
    'processing_time_ms': 45.2
}
```

### Score Interpretation

```
Fraud Score    Risk Level    Recommendation
0.0 - 0.3      Low          APPROVE
0.3 - 0.7      Medium       REVIEW
0.7 - 1.0      High         BLOCK

Default Threshold: 0.5
- Configurable via settings.FRAUD_THRESHOLD
- Can be adjusted based on business requirements
```

### Batch Prediction

```python
detector.batch_predict(transactions_df)
# Returns DataFrame with:
# - Original columns
# - fraud_score (0-1)
# - is_fraud (True/False)
# - risk_level ('low'/'medium'/'high')
```

### Performance

```
Latency: < 200ms per transaction (p99)
Throughput: 100+ requests/second
Batch: 200+ transactions/second
Memory: ~200MB for model + preprocessor
```

---

## Model Updates & Retraining

### When to Retrain

```
Triggers:
✓ Weekly: Fresh data available
✓ Monthly: Performance review
✓ On-demand: Model performance degradation
✓ When: New fraud patterns detected
✓ If: Distribution shift detected

Performance Degradation Thresholds:
- Recall drops below 0.90
- Precision drops below 0.75
- ROC-AUC drops below 0.90
```

### Retraining Process

```bash
# 1. Prepare new training data
python prepare_data.py --date-range 2024-01-01:2024-02-24

# 2. Train new model
python train_model.py --output-version 1.1.0

# 3. Evaluate and compare
# (Automatic, shows metrics vs current model)

# 4. If approved, push to production
# - Update MODEL_PATH in config
# - Restart API service
# - Monitor performance
```

### Versioning

```
Model Artifact Naming:
- best_model_v1.0.0.joblib
- preprocessor_v1.0.0.joblib

Version Convention:
MAJOR.MINOR.PATCH
- MAJOR: Algorithm change
- MINOR: Hyperparameter tuning
- PATCH: Bug fixes, data update
```

---

## Monitoring & Drift Detection

### Metrics to Monitor

```
1. Model Metrics (via analytics endpoint)
   - Current test set performance
   - Precision, Recall, F1, AUC
   
2. Production Metrics
   - Fraud rate (daily, weekly)
   - Alert rate (% flagged)
   - Model score distribution
   
3. Data Metrics
   - Transaction volume trends
   - Amount distribution
   - Merchant category distribution
   - Time patterns
   
4. System Metrics
   - Inference latency
   - API response times
   - Cache hit rates
```

### Drift Detection

```
Concept Drift: When fraud patterns change
Data Drift: When transaction patterns change

Detection Methods:
- KL divergence on score distribution
- Statistical tests on features (KS test)
- Performance degradation monitoring
```

---

## Troubleshooting

### Model Not Meeting Targets

```
If Recall < 0.95:
  ✓ Adjust fraud_threshold lower
  ✓ Increase SMOTE sampling ratio
  ✓ Try different algorithm (XGBoost usually best)
  ✓ Collect more fraud examples
  
If Precision < 0.80:
  ✓ Adjust fraud_threshold higher
  ✓ Increase hyperparameter regularization
  ✓ Reduce undersampling ratio
  ✓ Add more discriminative features
```

### Inference Errors

```
If score is NaN/inf:
  ✓ Check preprocessing for NaN values
  ✓ Verify feature scaling applied
  ✓ Check timestamp parsing
  
If latency > 200ms:
  ✓ Profile preprocessing
  ✓ Check model size
  ✓ Verify disk I/O not bottleneck
```

### Data Quality Issues

```
Missing values:
  ✓ Check transaction_location (optional)
  ✓ Validate timestamps

Outliers:
  ✓ Very large amounts
  ✓ Impossible timestamps
  ✓ Unknown merchant categories
```

---

## Advanced Topics

### Feature Importance

```python
# For tree-based models
importances = model.feature_importances_
feature_names = preprocessor.feature_names

for name, importance in zip(feature_names, importances):
    print(f"{name}: {importance:.4f}")

# Top features typically:
# - Amount and log-scaled amount
# - Hour of day
# - Merchant risk score
```

### Probability Calibration

```python
# Models should output well-calibrated probabilities
# (score ≈ actual fraud probability)

from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_test, y_pred_proba)
# plot to verify calibration
```

### Feature Interactions

```python
# Current system uses additive features
# Could add polynomial features for interactions:
# - interaction(amount, hour)
# - interaction(merchant_risk, hour)
```

---

## References

- [scikit-learn Documentation](https://scikit-learn.org/)
- [XGBoost Parameters](https://xgboost.readthedocs.io/)
- [imbalanced-learn SMOTE](https://imbalanced-learn.org/stable/over_sampling.html)
- [ROC-AUC vs PR-AUC](https://machinelearningmastery.com/roc-curves-and-auc/)

---

**Last Updated: 2024-02-24**
