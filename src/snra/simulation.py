from __future__ import annotations

import numpy as np
import pandas as pd

from .contract import SpatialDataset


def simulate_spatial_dataset(
    n_samples: int = 8,
    cells_per_sample: int = 180,
    planted: bool = True,
    seed: int = 1,
) -> SpatialDataset:
    """Generate a small spatial dataset with optional planted niche structure."""

    rng = np.random.default_rng(seed)
    coord_rows = []
    meta_rows = []
    labels = {}
    cell_types = np.array(["tumor", "macrophage", "tcell", "stromal"])
    for s in range(n_samples):
        sample_id = f"S{s+1:02d}"
        centers = np.array([[0.25, 0.25], [0.75, 0.25], [0.45, 0.75]])
        cluster = rng.choice(3, size=cells_per_sample, p=[0.35, 0.35, 0.30])
        coords = centers[cluster] + rng.normal(0, 0.10, size=(cells_per_sample, 2))
        coords = np.clip(coords, 0, 1)
        for i in range(cells_per_sample):
            unit_id = f"{sample_id}_C{i:04d}"
            x, y = coords[i]
            if planted and cluster[i] == 0:
                ct = rng.choice(["tumor", "macrophage"], p=[0.55, 0.45])
                niche = "tumor_macrophage_border"
            elif planted and cluster[i] == 1:
                ct = rng.choice(["tcell", "stromal"], p=[0.50, 0.50])
                niche = "immune_stromal_zone"
            else:
                ct = rng.choice(cell_types, p=[0.25, 0.25, 0.25, 0.25])
                niche = rng.choice(["background_a", "background_b"])
            if not planted:
                ct = rng.choice(cell_types)
                niche = rng.choice(
                    ["tumor_macrophage_border", "immune_stromal_zone", "background_a", "background_b"]
                )
            coord_rows.append({"unit_id": unit_id, "sample_id": sample_id, "x": x, "y": y})
            meta_rows.append({"unit_id": unit_id, "sample_id": sample_id, "cell_type": ct})
            labels[unit_id] = niche
    coord = pd.DataFrame(coord_rows)
    meta = pd.DataFrame(meta_rows)
    niche = pd.Series(labels, name="niche_label")
    niche.index.name = "unit_id"
    return SpatialDataset(coord, meta, niche)

