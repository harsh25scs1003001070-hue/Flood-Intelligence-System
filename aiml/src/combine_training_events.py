from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

files = [
    PROCESSED / "bihar_2024_09_27_training.csv",
    PROCESSED / "bihar_2022_09_02_training.csv",
]

frames = []

for path in files:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    frames.append(df)

combined = pd.concat(frames, ignore_index=True)

# Remove accidental duplicate rows.
combined = combined.drop_duplicates(
    subset=[
        "latitude",
        "longitude",
        "event_id",
    ]
)

output = PROCESSED / "final_flood_training.csv"

combined.to_csv(output, index=False)

print("Combined dataset created.")
print("Rows:", len(combined))
print("\nEvents:")
print(combined["event_id"].value_counts())

print("\nLabels:")
print(combined["flood_label"].value_counts())

print("\nMissing values:")
print(combined.isna().sum())