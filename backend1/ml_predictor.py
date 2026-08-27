from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "flood_risk_model.joblib"

FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_12h_mm",
    "rainfall_24h_mm",
]


# Load once when the backend starts.
artifact = joblib.load(MODEL_PATH)
model = artifact["model"]


def predict_ml_risk(
    rainfall_1h_mm: float,
    rainfall_3h_mm: float,
    rainfall_6h_mm: float,
    rainfall_12h_mm: float,
    rainfall_24h_mm: float,
) -> dict:

    X = pd.DataFrame([{
        "rainfall_1h_mm": rainfall_1h_mm,
        "rainfall_3h_mm": rainfall_3h_mm,
        "rainfall_6h_mm": rainfall_6h_mm,
        "rainfall_12h_mm": rainfall_12h_mm,
        "rainfall_24h_mm": rainfall_24h_mm,
    }])[FEATURES]

    score = float(model.predict_proba(X)[0, 1])

    if score >= 0.80:
        level = "CRITICAL"
    elif score >= 0.60:
        level = "HIGH"
    elif score >= 0.35:
        level = "MODERATE"
    else:
        level = "LOW"

    confidence = min(
        0.99,
        0.5 + abs(score - 0.5),
    )

    return {
        "risk_score": round(score, 4),
        "hazard_level": level,
        "confidence": round(confidence, 4),
    }