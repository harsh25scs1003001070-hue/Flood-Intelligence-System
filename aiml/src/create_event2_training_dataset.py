from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box


ROOT = Path(__file__).resolve().parents[1]

RAIN_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_2022_09_02_rainfall_features.csv"
)

FLOOD_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_2022_09_02_flood_labels.gpkg"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_2022_09_02_training.csv"
)

THRESHOLD = 0.10
HALF_CELL = 0.05


print("Loading Event 2 rainfall data...")

rainfall = pd.read_csv(RAIN_FILE)

print(f"Rainfall grid cells: {len(rainfall):,}")


print("\nBuilding IMERG grid-cell polygons...")

rain_geometries = [
    box(
        lon - HALF_CELL,
        lat - HALF_CELL,
        lon + HALF_CELL,
        lat + HALF_CELL,
    )
    for lon, lat in zip(
        rainfall["longitude"],
        rainfall["latitude"],
    )
]

rain_gdf = gpd.GeoDataFrame(
    rainfall.copy(),
    geometry=rain_geometries,
    crs="EPSG:4326",
)


print("\nLoading Event 2 flood polygons...")

flood_gdf = gpd.read_file(FLOOD_FILE)

if flood_gdf.empty:
    raise ValueError("Event 2 flood layer contains no polygons.")

print(f"Flood polygons: {len(flood_gdf):,}")

if flood_gdf.crs is None:
    raise ValueError("Flood layer has no CRS.")

if flood_gdf.crs.to_epsg() != 4326:
    flood_gdf = flood_gdf.to_crs(epsg=4326)


print("\nRepairing flood polygons...")

flood_gdf["geometry"] = flood_gdf.geometry.make_valid()

flood_gdf = flood_gdf[
    flood_gdf.geometry.notna()
    & ~flood_gdf.geometry.is_empty
].copy()

print(f"Valid polygons: {len(flood_gdf):,}")


print("\nCombining flood polygons...")

flood_union = flood_gdf.geometry.union_all()


print("\nCalculating flood overlap...")

overlap_fraction = []

for cell in rain_gdf.geometry:
    intersection = cell.intersection(flood_union)

    if intersection.is_empty:
        overlap_fraction.append(0.0)
    else:
        overlap_fraction.append(
            intersection.area / cell.area
        )

rain_gdf["flood_overlap_fraction"] = overlap_fraction

rain_gdf["flood_label"] = (
    rain_gdf["flood_overlap_fraction"] >= THRESHOLD
).astype(int)

rain_gdf["event_id"] = "BIHAR_2022_09_02"
rain_gdf["date"] = "2022-09-02"
rain_gdf["label_source"] = "NRSC_Sentinel1A"


training = rain_gdf.drop(columns=["geometry"])

training.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("EVENT 2 TRAINING DATASET CREATED")
print("========================================")

print(f"Output: {OUTPUT_FILE}")
print(f"Rows: {len(training):,}")

print("\nLabel distribution:")
print(training["flood_label"].value_counts().sort_index())

print("\nOverlap statistics:")
print(training["flood_overlap_fraction"].describe())

print("\nFlooded cells:")
print(
    training[training["flood_label"] == 1][
        [
            "latitude",
            "longitude",
            "flood_overlap_fraction",
        ]
    ].head(20)
)