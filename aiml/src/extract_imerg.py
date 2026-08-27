from pathlib import Path
import h5py
import numpy as np
import pandas as pd


# -------------------------------------------------
# Find the first IMERG file
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
# Read IMERG data
# -------------------------------------------------

with h5py.File(file_path, "r") as f:

    precipitation = f["Grid/precipitation"][0]
    lat = f["Grid/lat"][:]
    lon = f["Grid/lon"][:]
    time = f["Grid/time"][0]

    # IMERG commonly uses a fill value for missing data.
    # Convert invalid values to NaN.
    precipitation = precipitation.astype(float)

    fill_value = f["Grid/precipitation"].attrs.get("_FillValue")

    if fill_value is not None:
        precipitation[
            precipitation == fill_value
        ] = np.nan


# -------------------------------------------------
# Convert to dataframe
# -------------------------------------------------

lon_grid, lat_grid = np.meshgrid(lon, lat)

df = pd.DataFrame({
    "latitude": lat_grid.ravel(),
    "longitude": lon_grid.ravel(),
    "precipitation": precipitation.T.ravel(),
})


# Remove missing values
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

output_file = output_dir / "imerg_sample.csv"

df.to_csv(output_file, index=False)

print("\nExtraction complete.")
print(f"Rows saved: {len(df):,}")
print(f"Output: {output_file}")

print("\nSample:")
print(df.head())

print("\nRainfall statistics:")
print(df["precipitation"].describe())