from pathlib import Path
import h5py

data_dir = Path(__file__).resolve().parents[1] / "data" / "raw" / "rainfall"

files = list(data_dir.glob("*.HDF5")) + list(data_dir.glob("*.hdf5"))

if not files:
    raise FileNotFoundError(
        f"No HDF5 file found in: {data_dir}"
    )

file_path = files[0]

print(f"\nOpening file:\n{file_path}\n")

with h5py.File(file_path, "r") as f:

    def show(name, obj):
        if hasattr(obj, "shape"):
            print(f"{name}   shape={obj.shape}")
        else:
            print(name)

    f.visititems(show)