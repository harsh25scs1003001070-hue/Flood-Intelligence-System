from pathlib import Path
from datetime import datetime, timezone
import re

import h5py
import numpy as np
import pandas as pd


MIN_LAT = 24.0
MAX_LAT = 28.5

MIN_LON = 83.0
MAX_LON = 88.5

HALF_HOUR_MM = 0.5

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    ROOT
    / "data"
    / "raw"
    / "rainfall"
    / "BIHAR_2022_09_02"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_timestamp(filename: str) -> datetime:
    match = re.search(r"\.(\d{8})-S(\d{6})-E", filename)

    if not match:
        raise ValueError(
            f"Could not extract timestamp from: {filename}"
        )

    return datetime.strptime(
        match.group(1) + match.group(2),
        "%Y%m%d%H%M%S",
    ).replace(tzinfo=timezone.utc)


# ------------------------------------------------------------
# FIND FILES
# ------------------------------------------------------------

files = sorted(
    {
        p.resolve()
        for p in DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".hdf5"
    }
)

if not files:
    raise FileNotFoundError(
        f"No HDF5 files found in: {DATA_DIR}"
    )

print(f"Found {len(files)} HDF5 files.")

if len(files) != 48:
    raise ValueError(
        f"Expected 48 files, found {len(files)}."
    )


# ------------------------------------------------------------
# SORT + CHECK CONTINUITY
# ------------------------------------------------------------

file_times = sorted(
    [(extract_timestamp(p.name), p) for p in files],
    key=lambda x: x[0],
)

timestamps = [t for t, _ in file_times]

print("First timestamp:", timestamps[0])
print("Last timestamp :", timestamps[-1])

for i in range(1, len(timestamps)):
    gap = (
        pd.Timestamp(timestamps[i])
        - pd.Timestamp(timestamps[i - 1])
    )

    if gap != pd.Timedelta(minutes=30):
        raise ValueError(
            f"Timestamp gap detected:\n"
            f"{timestamps[i-1]} → {timestamps[i]}\n"
            f"Gap: {gap}"
        )

print("Timestamp continuity check: PASSED")


# ------------------------------------------------------------
# GET REGIONAL GRID
# ------------------------------------------------------------

with h5py.File(file_times[0][1], "r") as f:
    lat = f["Grid/lat"][:]
    lon = f["Grid/lon"][:]

lat_idx = np.where(
    (lat >= MIN_LAT) & (lat <= MAX_LAT)
)[0]

lon_idx = np.where(
    (lon >= MIN_LON) & (lon <= MAX_LON)
)[0]

regional_lat = lat[lat_idx]
regional_lon = lon[lon_idx]


# ------------------------------------------------------------
# READ 48 FILES
# ------------------------------------------------------------

frames = []

for i, (timestamp, file_path) in enumerate(
    file_times,
    start=1,
):
    print(
        f"[{i}/48] {timestamp.isoformat()} "
        f"{file_path.name}"
    )

    with h5py.File(file_path, "r") as f:

        dataset = f["Grid/precipitation"]

        precipitation = dataset[0].astype(float)

        fill_value = dataset.attrs.get("_FillValue")

        if fill_value is not None:
            precipitation[
                precipitation == fill_value
            ] = np.nan

        regional = precipitation[
            np.ix_(lon_idx, lat_idx)
        ]

        rainfall_mm = (
            regional * HALF_HOUR_MM
        ).T

        frames.append(rainfall_mm)


rainfall = np.stack(frames)


# ------------------------------------------------------------
# ACCUMULATIONS
# ------------------------------------------------------------

rainfall_1h = rainfall[:2].sum(axis=0)
rainfall_3h = rainfall[:6].sum(axis=0)
rainfall_6h = rainfall[:12].sum(axis=0)
rainfall_12h = rainfall[:24].sum(axis=0)
rainfall_24h = rainfall[:48].sum(axis=0)


# ------------------------------------------------------------
# DATAFRAME
# ------------------------------------------------------------

lon_grid, lat_grid = np.meshgrid(
    regional_lon,
    regional_lat,
)

df = pd.DataFrame({
    "latitude": lat_grid.ravel(),
    "longitude": lon_grid.ravel(),
    "rainfall_1h_mm": rainfall_1h.ravel(),
    "rainfall_3h_mm": rainfall_3h.ravel(),
    "rainfall_6h_mm": rainfall_6h.ravel(),
    "rainfall_12h_mm": rainfall_12h.ravel(),
    "rainfall_24h_mm": rainfall_24h.ravel(),
})


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

output_file = (
    OUTPUT_DIR
    / "bihar_2022_09_02_rainfall_features.csv"
)

df.to_csv(output_file, index=False)

print("\n========================================")
print("EVENT 2 RAINFALL FEATURES COMPLETE")
print("========================================")
print(f"Rows saved: {len(df):,}")
print(f"Output: {output_file}")

print("\nSample:")
print(df.head())

print("\nMissing values:")
print(df.isna().sum())