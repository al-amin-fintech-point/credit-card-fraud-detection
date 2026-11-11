"""Validation and EDA utilities for the public Kaggle dataset."""
from pathlib import Path
import pandas as pd

FEATURES = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount"]
TARGET = "Class"
REQUIRED_COLUMNS = [*FEATURES, TARGET]


class DatasetError(ValueError):
    """Raised when a training dataset is absent or invalid."""


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Read and validate a Kaggle-format CSV without modifying source data."""
    path = Path(path)
    if not path.is_file():
        raise DatasetError(f"Dataset not found: {path}. See README.md for Kaggle setup.")
    try:
        frame = pd.read_csv(path)
    except Exception as exc:
        raise DatasetError(f"Could not read CSV: {exc}") from exc
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise DatasetError(f"Dataset is missing required columns: {', '.join(missing)}")
    frame = frame[REQUIRED_COLUMNS].copy()
    for column in REQUIRED_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame.isna().any().any():
        raise DatasetError("Dataset contains missing or non-numeric required values.")
    if not frame[TARGET].isin([0, 1]).all():
        raise DatasetError("Class must contain only 0 (legitimate) and 1 (fraud).")
    if (frame["Amount"] < 0).any() or (frame["Time"] < 0).any():
        raise DatasetError("Time and Amount must be non-negative.")
    if frame.empty or frame[TARGET].nunique() != 2:
        raise DatasetError("Dataset must contain both classes and at least one row.")
    return frame


def dataset_summary(frame: pd.DataFrame) -> dict:
    """Return concise quality and class balance statistics."""
    counts = frame[TARGET].value_counts().to_dict()
    return {"rows": len(frame), "columns": len(frame.columns),
            "duplicates": int(frame.duplicated().sum()),
            "missing_values": int(frame.isna().sum().sum()),
            "legitimate": int(counts.get(0, 0)), "fraud": int(counts.get(1, 0)),
            "fraud_rate": float(frame[TARGET].mean())}
