from __future__ import annotations
from typing import Iterable
import pandas as pd

FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_12h_mm",
    "rainfall_24h_mm",
    "water_level_m",
    "water_level_change_m_per_h",
    "elevation_m",
    "slope_deg",
    "distance_to_river_m",
    "drainage_density",
    "population_density",
    "built_up_pct",
    "critical_asset_count",
]

def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in FEATURES + ["flood_label", "event_id"] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

def make_X(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)
    return df[FEATURES].copy()

def make_y(df: pd.DataFrame) -> pd.Series:
    validate_columns(df)
    return df["flood_label"].astype(int).copy()
