from __future__ import annotations
import argparse
import json
import joblib
import pandas as pd

FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_12h_mm",
    "rainfall_24h_mm",
]

def level(score: float) -> str:
    if score >= 0.80:
        return "CRITICAL"
    if score >= 0.60:
        return "HIGH"
    if score >= 0.35:
        return "MODERATE"
    return "LOW"

def predict_risk(features: dict, model_path: str = "models/flood_risk_model.joblib") -> dict:
    artifact = joblib.load(model_path)
    model = artifact["model"]
    X = pd.DataFrame([{name: features.get(name) for name in FEATURES}])
    score = float(model.predict_proba(X)[:, 1][0])

    # Conservative UI confidence proxy. For a production model,
    # replace this with a calibrated uncertainty method.
    confidence = float(min(0.99, 0.5 + abs(score - 0.5)))

    return {
        "risk_score": round(score, 4),
        "hazard_level": level(score),
        "confidence": round(confidence, 4),
    }

if __name__ == "__main__":

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--model",
        default="models/flood_risk_model.joblib",
    )

    args = ap.parse_args()

    demo = {
        "rainfall_1h_mm": 60,
        "rainfall_3h_mm": 120,
        "rainfall_6h_mm": 180,
        "rainfall_12h_mm": 240,
        "rainfall_24h_mm": 310,
    }

    print(
        json.dumps(
            predict_risk(
                demo,
                args.model,
            ),
            indent=2,
        )
    )