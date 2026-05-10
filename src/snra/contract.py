from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class SpatialDataset:
    """Minimal SNRA input object.

    The statistical unit is `sample_id`. Cells or spots are nested inside
    samples; no certificate may be calibrated at the cell-only level.
    """

    coordinates: pd.DataFrame
    metadata: pd.DataFrame
    niche_labels: pd.Series


REQUIRED_COORD_COLUMNS = ("unit_id", "sample_id", "x", "y")
REQUIRED_META_COLUMNS = ("unit_id", "sample_id", "cell_type")


def _missing_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
    return [col for col in required if col not in df.columns]


def validate_dataset(dataset: SpatialDataset, min_samples: int = 2) -> dict[str, object]:
    """Validate minimal input contract and return an audit-ready report."""

    errors: list[str] = []
    warnings: list[str] = []
    coord = dataset.coordinates.copy()
    meta = dataset.metadata.copy()
    labels = dataset.niche_labels.copy()

    miss_coord = _missing_columns(coord, REQUIRED_COORD_COLUMNS)
    miss_meta = _missing_columns(meta, REQUIRED_META_COLUMNS)
    if miss_coord:
        errors.append(f"coordinates missing columns: {','.join(miss_coord)}")
    if miss_meta:
        errors.append(f"metadata missing columns: {','.join(miss_meta)}")
    if labels.name is None:
        labels.name = "niche_label"
    if labels.index.name != "unit_id":
        labels.index.name = "unit_id"

    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    coord_ids = set(coord["unit_id"].astype(str))
    meta_ids = set(meta["unit_id"].astype(str))
    label_ids = set(labels.index.astype(str))
    common = coord_ids & meta_ids & label_ids
    if len(common) == 0:
        errors.append("no shared unit_id across coordinates, metadata, and niche labels")
    if len(common) < min(len(coord_ids), len(meta_ids), len(label_ids)):
        warnings.append("some units are missing in at least one input table")

    sample_count = coord.loc[coord["unit_id"].astype(str).isin(common), "sample_id"].nunique()
    if sample_count < min_samples:
        errors.append(
            f"sample-level calibration requires >= {min_samples} samples, observed {sample_count}"
        )

    xy = coord[["x", "y"]].to_numpy(dtype=float)
    if not np.isfinite(xy).all():
        errors.append("coordinates contain non-finite x/y values")
    if coord[["x", "y"]].drop_duplicates().shape[0] < 3:
        errors.append("not enough unique spatial coordinates to build a spatial graph")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "n_units": len(common),
        "n_samples": int(sample_count),
        "n_cell_types": int(meta["cell_type"].nunique()),
        "n_niches": int(labels.nunique()),
    }

