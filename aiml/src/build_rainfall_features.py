from pathlib import Path
from datetime import datetime, timezone
import re

import h5py
import numpy as np
import pandas as pd


# ============================================================
# STUDY REGION: BIHAR / GANGA FLOOD REGION
# ============================================================

MIN_LAT = 24.0
MAX_LAT = 28.5

MIN_LON = 83.0
MAX_LON = 88.5

HALF_HOUR_MM = 0.5


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = (
    ROOT
    / "data"
    / "raw"
    / "rainfall"
    / "BIHAR_2024_09_27"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# EXTRACT TIMESTAMP FROM IMERG FILENAME
# ============================================================

def extract_timestamp(filename: str) -> datetime:
    """
    Example:
    3B-HHR.MS.MRG.3IMERG.20240222-S233000-E235959.1410.V07B.HDF5
    """

    match = re.search(r"\.(\d{8})-S(\d{6})-E", filename)

    if not match:
        raise ValueError(
            f"Could not extract timestamp from: {filename}"
        )

    date_part = match.group(1)
    time_part = match.group(2)

    dt = datetime.strptime(
        date_part + time_part,
        "%Y%m%d%H%M%S",
    )

    return dt.replace(tzinfo=timezone.utc)


# ============================================================
# FIND FILES
# ============================================================
files = sorted(
    {
        p.resolve()
        for p in DATA_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".hdf5"
    }
)
if not files:
    raise FileNotFoundError(
        f"No HDF5 files found in:\n{DATA_DIR}"
    )

print(f"Found {len(files)} HDF5 files.")


# ============================================================
# SORT BY ACTUAL TIME
# ============================================================

file_times = []

for file_path in files:
    timestamp = extract_timestamp(file_path.name)
    file_times.append((timestamp, file_path))

file_times.sort(key=lambda x: x[0])


# ============================================================
# CHECK TIME CONTINUITY
# ============================================================

timestamps = [t for t, _ in file_times]

print("\nFirst timestamp:", timestamps[0])
print("Last timestamp :", timestamps[-1])


expected_delta = pd.Timedelta(minutes=30)

for i in range(1, len(timestamps)):

    actual_delta = (
        pd.Timestamp(timestamps[i])
        - pd.Timestamp(timestamps[i - 1])
    )

    if actual_delta != expected_delta:

        raise ValueError(
            "\nTimestamp gap detected!\n"
            f"Previous: {timestamps[i - 1]}\n"
            f"Current : {timestamps[i]}\n"
            f"Gap     : {actual_delta}\n"
            "\nThe files must be consecutive 30-minute observations."
        )

print("\nTimestamp continuity check: PASSED")


# ============================================================
# READ GRID FROM FIRST FILE
# ============================================================

first_file = file_times[0][1]

with h5py.File(first_file, "r") as f:

    lat = f["Grid/lat"][:]
    lon = f["Grid/lon"][:]

lat_mask = (lat >= MIN_LAT) & (lat <= MAX_LAT)
lon_mask = (lon >= MIN_LON) & (lon <= MAX_LON)

lat_idx = np.where(lat_mask)[0]
lon_idx = np.where(lon_mask)[0]

if len(lat_idx) == 0 or len(lon_idx) == 0:

    raise ValueError(
        "Study region does not overlap IMERG grid."
    )

regional_lat = lat[lat_idx]
regional_lon = lon[lon_idx]

print(
    f"\nRegional grid: "
    f"{len(regional_lat)} lat × "
    f"{len(regional_lon)} lon"
)


# ============================================================
# READ ALL HALF-HOUR DATA
# ============================================================

rainfall_frames = []

for index, (timestamp, file_path) in enumerate(
    file_times,
    start=1,
):

    print(
        f"[{index}/{len(file_times)}] "
        f"{timestamp.isoformat()} "
        f"{file_path.name}"
    )

    with h5py.File(file_path, "r") as f:

        dataset = f["Grid/precipitation"]

        precipitation = (
            dataset[0]
            .astype(np.float64)
        )

        fill_value = dataset.attrs.get(
            "_FillValue"
        )

        if fill_value is not None:

            precipitation[
                precipitation == fill_value
            ] = np.nan

        # ----------------------------------------------------
        # Crop Bihar region
        # ----------------------------------------------------

        regional = precipitation[
            np.ix_(
                lon_idx,
                lat_idx
            )
        ]

        # ----------------------------------------------------
        # Convert mm/hr → mm per 30 minutes
        # ----------------------------------------------------

        rainfall_mm = (
            regional * HALF_HOUR_MM
        )

        # Dataset is [lon, lat]
        # We want [lat, lon]

        rainfall_mm = rainfall_mm.T

        rainfall_frames.append(
            rainfall_mm
        )


# ============================================================
# STACK:
# time × latitude × longitude
# ============================================================

rainfall = np.stack(
    rainfall_frames
)

print(
    "\nRainfall array shape:",
    rainfall.shape
)


# ============================================================
# REQUIRE AT LEAST 48 HALF-HOURLY FILES
# ============================================================

if len(rainfall) < 48:

    raise ValueError(
        f"Need at least 48 consecutive files "
        f"for a 24-hour window. Found {len(rainfall)}."
    )


# ============================================================
# USE FIRST 48 FILES = 24 HOURS
# ============================================================

rainfall_24h_data = rainfall[:48]


# ============================================================
# RAINFALL ACCUMULATIONS
# ============================================================

rainfall_1h = np.sum(
    rainfall_24h_data[:2],
    axis=0,
)

rainfall_3h = np.sum(
    rainfall_24h_data[:6],
    axis=0,
)

rainfall_6h = np.sum(
    rainfall_24h_data[:12],
    axis=0,
)

rainfall_12h = np.sum(
    rainfall_24h_data[:24],
    axis=0,
)

rainfall_24h = np.sum(
    rainfall_24h_data[:48],
    axis=0,
)


# ============================================================
# GRID
# ============================================================

lon_grid, lat_grid = np.meshgrid(
    regional_lon,
    regional_lat,
)


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame({
    "latitude": lat_grid.ravel(),
    "longitude": lon_grid.ravel(),

    "rainfall_1h_mm":
        rainfall_1h.ravel(),

    "rainfall_3h_mm":
        rainfall_3h.ravel(),

    "rainfall_6h_mm":
        rainfall_6h.ravel(),

    "rainfall_12h_mm":
        rainfall_12h.ravel(),

    "rainfall_24h_mm":
        rainfall_24h.ravel(),
})


# ============================================================
# SAVE
# ============================================================

output_file = (
    OUTPUT_DIR /
    "bihar_rainfall_features.csv"
)

df.to_csv(
    output_file,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================
print("\n========================================")
print("RAINFALL FEATURE GENERATION COMPLETE")
print("========================================")

print(f"Rows saved: {len(df):,}")
print(f"Output: {output_file}")

print("\nFeature summary:")

print(
    df[
        [
            "rainfall_1h_mm",
            "rainfall_3h_mm",
            "rainfall_6h_mm",
            "rainfall_12h_mm",
            "rainfall_24h_mm",
        ]
    ].describe()
)


print(
    f"Rows saved: {len(df):,}"
)

print(
    f"Output: {output_file}"
)

print("\nFeature summary:")

print(
    df[
        [
            "rainfall_1h_mm",
            "rainfall_3h_mm",
            "rainfall_6h_mm",
            "rainfall_12h_mm",
            "rainfall_24h_mm",
        ]
    ].describe()
)