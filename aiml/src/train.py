from __future__ import annotations
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from features import FEATURES, make_X, make_y


def train(csv_path: str, model_path: str) -> None:
    df = pd.read_csv(csv_path)
    X = make_X(df)
    y = make_y(df)

    # Group split prevents rows from the same flood event leaking into test.
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=df["event_id"]))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    pre = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                FEATURES,
            )
        ],
        remainder="drop",
    )

    pos = max(1, int(y_train.sum()))
    neg = max(1, int(len(y_train) - y_train.sum()))
    scale_pos_weight = neg / pos

    base = XGBClassifier(
        n_estimators=450,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=2.0,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
        scale_pos_weight=scale_pos_weight,
    )

    uncalibrated = Pipeline([
        ("pre", pre),
        ("model", base),
    ])

    uncalibrated.fit(X_train, y_train)
    p = uncalibrated.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, p)),
        "pr_auc": float(average_precision_score(y_test, p)),
        "precision_at_0_5": float(precision_score(y_test, p >= 0.5, zero_division=0)),
        "recall_at_0_5": float(recall_score(y_test, p >= 0.5, zero_division=0)),
        "f1_at_0_5": float(f1_score(y_test, p >= 0.5, zero_division=0)),
        "n_train": int(len(train_idx)),
        "n_test": int(len(test_idx)),
        "n_events_train": int(df.iloc[train_idx]["event_id"].nunique()),
        "n_events_test": int(df.iloc[test_idx]["event_id"].nunique()),
    }

    # Calibrate the probability estimates. The model artifact remains one pipeline.
    calibrated = CalibratedClassifierCV(
        estimator=uncalibrated,
        method="sigmoid",
        cv=3,
    )
    calibrated.fit(X_train, y_train)

    out = Path(model_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": calibrated,
        "features": FEATURES,
        "metrics": metrics,
        "version": "0.1.0",
    }
    joblib.dump(artifact, out)

    print(json.dumps(metrics, indent=2))
    print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--model", default="models/flood_risk_model.joblib")
    args = parser.parse_args()
    train(args.csv, args.model)
