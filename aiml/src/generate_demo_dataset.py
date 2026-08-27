from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

def make_data(n_events: int = 120, locations_per_event: int = 30) -> pd.DataFrame:
    rows = []
    for e in range(n_events):
        event_id = f"E{e:04d}"
        event_factor = RNG.beta(2.0, 5.0)

        for j in range(locations_per_event):
            loc = f"L{j:03d}"
            rainfall_1h = max(0, RNG.gamma(2.2, 12) + 70 * event_factor)
            rainfall_3h = max(rainfall_1h, rainfall_1h * RNG.uniform(1.4, 2.4))
            rainfall_6h = rainfall_3h * RNG.uniform(1.3, 1.9)
            rainfall_12h = rainfall_6h * RNG.uniform(1.2, 1.7)
            rainfall_24h = rainfall_12h * RNG.uniform(1.2, 1.7)

            elevation = RNG.uniform(100, 500)
            slope = RNG.uniform(0.2, 8.0)
            river_dist = RNG.uniform(50, 5000)
            water_level = max(0, RNG.normal(3.5 + 6*event_factor, 1.2))
            water_change = max(-1, RNG.normal(0.6 + 1.8*event_factor, 0.5))
            drainage = RNG.uniform(0.1, 0.95)
            pop_density = RNG.lognormal(mean=7.2, sigma=0.8)
            built = np.clip(RNG.normal(55, 20), 5, 98)
            critical = RNG.poisson(2)

            # Synthetic label only for plumbing tests. Not scientifically valid.
            z = (
                0.018 * rainfall_6h
                + 0.55 * water_level
                + 1.20 * water_change
                + 0.8 * drainage
                + 0.010 * built
                + 0.000015 * pop_density
                - 0.0012 * elevation
                - 0.00015 * river_dist
                - 0.05 * slope
                + 0.12 * critical
                - 4.2
            )
            p = 1 / (1 + np.exp(-z))
            flood = int(RNG.random() < p)

            rows.append({
                "rainfall_1h_mm": rainfall_1h,
                "rainfall_3h_mm": rainfall_3h,
                "rainfall_6h_mm": rainfall_6h,
                "rainfall_12h_mm": rainfall_12h,
                "rainfall_24h_mm": rainfall_24h,
                "water_level_m": water_level,
                "water_level_change_m_per_h": water_change,
                "elevation_m": elevation,
                "slope_deg": slope,
                "distance_to_river_m": river_dist,
                "drainage_density": drainage,
                "population_density": pop_density,
                "built_up_pct": built,
                "critical_asset_count": critical,
                "flood_label": flood,
                "event_id": event_id,
                "timestamp": f"2025-{(e//10)%12+1:02d}-{(e%27)+1:02d}",
                "location_id": loc,
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "demo_train.csv"
    df = make_data()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}")
