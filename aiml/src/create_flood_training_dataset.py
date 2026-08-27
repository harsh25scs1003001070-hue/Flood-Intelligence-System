from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAIN_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_rainfall_features.csv"
)

FLOOD_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_flood_labels.gpkg"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "bihar_2024_09_27_training.csv"
)


# ------------------------------------------------------------
# LOAD RAINFALL DATA
# ------------------------------------------------------------

print("Loading rainfall data...")

rainfall = pd.read_csv(RAIN_FILE)

required = [
    "latitude",
    "longitude",
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_12h_mm",
    "rainfall_24h_mm",
]

missing = [c for c in required if c not in rainfall.columns]

if missing:
    raise ValueError(f"Missing rainfall columns: {missing}")

print(f"Rainfall grid cells: {len(rainfall):,}")


# ------------------------------------------------------------
# BUILD 0.1 DEGREE GRID-CELL POLYGONS
# ------------------------------------------------------------

print("\nBuilding IMERG grid-cell polygons...")

# IMERG cell centers are ~0.1 degree apart.
HALF_CELL = 0.05

rain_geometries = []

for lon, lat in zip(
    rainfall["longitude"],
    rainfall["latitude"],
):
    rain_geometries.append(
        box(
            lon - HALF_CELL,
            lat - HALF_CELL,
            lon + HALF_CELL,
            lat + HALF_CELL,
        )
    )

rain_gdf = gpd.GeoDataFrame(
    rainfall.copy(),
    geometry=rain_geometries,
    crs="EPSG:4326",
)


# ------------------------------------------------------------
# LOAD FLOOD POLYGONS
# ------------------------------------------------------------

print("\nLoading flood polygons...")

flood_gdf = gpd.read_file(FLOOD_FILE)

if flood_gdf.empty:
    raise ValueError("Flood GeoPackage contains no polygons.")

print(f"Flood polygons: {len(flood_gdf):,}")

if flood_gdf.crs is None:
    raise ValueError(
        "Flood layer has no CRS. Set it to EPSG:4326."
    )

if flood_gdf.crs.to_epsg() != 4326:
    flood_gdf = flood_gdf.to_crs(epsg=4326)


# ------------------------------------------------------------
# UNION FLOOD POLYGONS
# ------------------------------------------------------------
print("\nChecking and repairing flood polygons...")

# Repair invalid polygon geometries.
flood_gdf["geometry"] = flood_gdf.geometry.make_valid()

# Remove empty geometries.
flood_gdf = flood_gdf[
    flood_gdf.geometry.notna()
    & ~flood_gdf.geometry.is_empty
].copy()

print(
    "Valid polygons after repair:",
    len(flood_gdf),
)

print("\nCombining flood polygons...")

flood_union = flood_gdf.geometry.union_all()


# ------------------------------------------------------------
# INTERSECTION AREA
# ------------------------------------------------------------

print("\nCalculating flood overlap...")

overlap_fraction = []

for cell in rain_gdf.geometry:

    intersection = cell.intersection(flood_union)

    if intersection.is_empty:
        overlap_fraction.append(0.0)
        continue

    fraction = (
        intersection.area / cell.area
    )

    overlap_fraction.append(fraction)


rain_gdf["flood_overlap_fraction"] = overlap_fraction


# ------------------------------------------------------------
# LABEL
# ------------------------------------------------------------

# Conservative first threshold:
# 10% of cell must overlap flood polygon.
THRESHOLD = 0.10

rain_gdf["flood_label"] = (
    rain_gdf["flood_overlap_fraction"] >= THRESHOLD
).astype(int)


# ------------------------------------------------------------
# EVENT METADATA
# ------------------------------------------------------------

rain_gdf["event_id"] = "BIHAR_2024_09_27"
rain_gdf["date"] = "2024-09-27"
rain_gdf["label_source"] = "NRSC_Sentinel1A"


# ------------------------------------------------------------
# REMOVE GEOMETRY
# ------------------------------------------------------------

training = rain_gdf.drop(
    columns=["geometry"]
)


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

training.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("TRAINING DATASET CREATED")
print("========================================")

print(f"Output: {OUTPUT_FILE}")
print(f"Rows: {len(training):,}")

print("\nLabel distribution:")
print(
    training["flood_label"]
    .value_counts()
    .sort_index()
)

print("\nOverlap statistics:")
print(
    training["flood_overlap_fraction"].describe()
)

print("\nFlooded cells:")
print(
    training[
        training["flood_label"] == 1
    ][
        [
            "latitude",
            "longitude",
            "flood_overlap_fraction",
        ]
    ].head(20)
)