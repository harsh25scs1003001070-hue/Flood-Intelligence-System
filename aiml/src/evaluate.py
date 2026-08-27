from __future__ import annotations
import argparse
import json
import joblib
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from features import make_X, make_y

def main(csv_path: str, model_path: str):
    artifact = joblib.load(model_path)
    model = artifact["model"]
    df = pd.read_csv(csv_path)

    X = make_X(df)
    y = make_y(df)
    p = model.predict_proba(X)[:, 1]
    pred = (p >= 0.5).astype(int)

    result = {
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--model", required=True)
    args = ap.parse_args()
    main(args.csv, args.model)
