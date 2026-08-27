from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT
    / "data"
    / "processed"
    / "final_flood_training.csv"
)

MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "flood_risk_model.joblib"


FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_12h_mm",
    "rainfall_24h_mm",
]

TARGET = "flood_label"


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("Loading combined training data...")

df = pd.read_csv(DATA_FILE)

missing = [
    c for c in FEATURES + [TARGET, "event_id"]
    if c not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

print(f"Rows: {len(df):,}")

print("\nEvents:")
print(df["event_id"].value_counts())

print("\nLabels:")
print(df[TARGET].value_counts())


# ------------------------------------------------------------
# EVENT-BASED SPLIT
# ------------------------------------------------------------
# For the hackathon MVP, train on 2022 and test on 2024.
# This is deliberately event-based rather than random.

TRAIN_EVENT = "BIHAR_2022_09_02"
TEST_EVENT = "BIHAR_2024_09_27"

train_df = df[
    df["event_id"] == TRAIN_EVENT
].copy()

test_df = df[
    df["event_id"] == TEST_EVENT
].copy()

if train_df.empty:
    raise ValueError(
        f"No training rows for {TRAIN_EVENT}"
    )

if test_df.empty:
    raise ValueError(
        f"No test rows for {TEST_EVENT}"
    )

print("\nTraining event:")
print(TRAIN_EVENT)

print("Test event:")
print(TEST_EVENT)


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ------------------------------------------------------------
# CLASS IMBALANCE
# ------------------------------------------------------------

positive = (y_train == 1).sum()
negative = (y_train == 0).sum()

if positive == 0:
    raise ValueError(
        "Training event contains no positive flood examples."
    )

scale_pos_weight = negative / positive

print("\nTraining label counts:")
print(y_train.value_counts())

print(
    f"\nscale_pos_weight = "
    f"{scale_pos_weight:.3f}"
)


# ------------------------------------------------------------
# TRAIN XGBOOST
# ------------------------------------------------------------

print("\nTraining XGBoost model...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
)


# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

probabilities = model.predict_proba(
    X_test
)[:, 1]

predictions = (
    probabilities >= 0.5
).astype(int)


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

print("\n========================================")
print("MODEL EVALUATION")
print("========================================")

print(
    "Accuracy:",
    accuracy_score(y_test, predictions)
)

print(
    "Precision:",
    precision_score(
        y_test,
        predictions,
        zero_division=0,
    )
)

print(
    "Recall:",
    recall_score(
        y_test,
        predictions,
        zero_division=0,
    )
)

print(
    "F1:",
    f1_score(
        y_test,
        predictions,
        zero_division=0,
    )
)

try:
    print(
        "ROC-AUC:",
        roc_auc_score(
            y_test,
            probabilities,
        )
    )
except ValueError:
    print(
        "ROC-AUC: unavailable "
        "(only one test class present)"
    )


print("\nConfusion matrix:")
print(
    confusion_matrix(
        y_test,
        predictions,
    )
)

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0,
    )
)


# ------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------

print("\nFeature importance:")

importance = pd.Series(
    model.feature_importances_,
    index=FEATURES,
).sort_values(ascending=False)

print(importance)


# ------------------------------------------------------------
# SAVE MODEL
# ------------------------------------------------------------
artifact = {
    "model": model,
    "features": FEATURES,
    "model_type": "XGBClassifier",
    "train_event": TRAIN_EVENT,
    "test_event": TEST_EVENT,
}

joblib.dump(
    artifact,
    MODEL_FILE,
)

print("\n========================================")
print("MODEL SAVED")
print("========================================")
print(f"Model: {MODEL_FILE}")
artifact = {
    "model": model,
    "features": FEATURES,
    "model_type": "XGBClassifier",
    "train_event": TRAIN_EVENT,
    "test_event": TEST_EVENT,
}

joblib.dump(
    artifact,
    MODEL_FILE,
)

print(f"Model saved: {MODEL_FILE}")