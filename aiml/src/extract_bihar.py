from pathlib import Path
import h5py
import numpy as np
import pandas as pd


# -------------------------------------------------
# STUDY REGION: BIHAR / GANGA FLOOD REGION
# -------------------------------------------------

MIN_LAT = 24.0
MAX_LAT = 28.5

MIN_LON = 83.0
MAX_LON = 88.5


# -------------------------------------------------
# Locate IMERG file
# -------------------------------------------------

data_dir = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "rainfall"
)

files = list(data_dir.glob("*.HDF5")) + list(data_dir.glob("*.hdf5"))

if not files:
    raise FileNotFoundError(
        f"No HDF5 file found in: {data_dir}"
    )

file_path = files[0]

print(f"Reading: {file_path.name}")


# -------------------------------------------------
# Read HDF5
# -------------------------------------------------

with h5py.File(file_path, "r") as f:

    precipitation = f["Grid/precipitation"][0].astype(float)
    lat = f["Grid/lat"][:]
    lon = f["Grid/lon"][:]

    # Convert fill values to NaN
    fill_value = f["Grid/precipitation"].attrs.get("_FillValue")

    if fill_value is not None:
        precipitation[precipitation == fill_value] = np.nan


# -------------------------------------------------
# Find regional indices
# -------------------------------------------------

lat_mask = (lat >= MIN_LAT) & (lat <= MAX_LAT)
lon_mask = (lon >= MIN_LON) & (lon <= MAX_LON)

lat_idx = np.where(lat_mask)[0]
lon_idx = np.where(lon_mask)[0]

if len(lat_idx) == 0 or len(lon_idx) == 0:
    raise ValueError("Study region does not overlap the dataset.")


# -------------------------------------------------
# Crop precipitation
# -------------------------------------------------

regional_precipitation = precipitation[
    np.ix_(lon_idx, lat_idx)
]

regional_lat = lat[lat_idx]
regional_lon = lon[lon_idx]


# -------------------------------------------------
# Build grid
# -------------------------------------------------

lon_grid, lat_grid = np.meshgrid(
    regional_lon,
    regional_lat
)


# precipitation shape is [lon, lat],
# so transpose it to [lat, lon]
regional_precipitation = regional_precipitation.T


df = pd.DataFrame({
    "latitude": lat_grid.ravel(),
    "longitude": lon_grid.ravel(),
    "precipitation": regional_precipitation.ravel(),
})

df = df.dropna(subset=["precipitation"])


# -------------------------------------------------
# Save
# -------------------------------------------------

output_dir = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
)

output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "bihar_imerg_sample.csv"

df.to_csv(output_file, index=False)

print("\nRegional extraction complete.")
print(f"Rows saved: {len(df):,}")
print(f"Latitude range: {df['latitude'].min()} → {df['latitude'].max()}")
print(f"Longitude range: {df['longitude'].min()} → {df['longitude'].max()}")
print(f"Output: {output_file}")

print("\nSample:")
print(df.head())