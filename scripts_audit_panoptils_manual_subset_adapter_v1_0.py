#!/usr/bin/env python
"""Build a minimal SNRA adapter audit for PanopTILs manual annotations.

The adapter intentionally treats PanopTILs as an orthogonal histopathology
validation layer, not a spatial-omics molecular dataset.  It checks whether
manual nuclei labels and manual region masks can support a cell-level
tumor/stroma/TIL geometry audit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


REGION_CODE = {
    0: "Exclude",
    1: "Cancerous_epithelium",
    2: "Stroma",
    3: "TILs_region",
    4: "Normal_epithelium",
    5: "Junk_Debris",
    6: "Blood",
    7: "Other",
    8: "Whitespace_Empty",
}

CELL_GROUP = {
    "CancerEpithelium": "cancer_cell",
    "StromalCellNOS": "stromal_cell",
    "ActiveStromalCellNOS": "stromal_cell",
    "TILsCell": "til_cell",
    "ActiveTILsCell": "til_cell",
    "OtherCell": "other_cell",
    "UnknownOrAmbiguousCell": "unknown_cell",
}


def centroid_from_coords(row: pd.Series) -> tuple[float, float]:
    try:
        xs = [float(x) for x in str(row["coords_x"]).split(",") if x != ""]
        ys = [float(y) for y in str(row["coords_y"]).split(",") if y != ""]
        if xs and ys:
            return float(np.mean(xs)), float(np.mean(ys))
    except Exception:
        pass
    return (float(row["left"] + row["right"]) / 2.0, float(row["top"] + row["bottom"]) / 2.0)


def read_mask_region(mask_path: Path) -> np.ndarray | None:
    if not mask_path.exists():
        return None
    img = np.asarray(Image.open(mask_path))
    if img.ndim == 3:
        return img[:, :, 0]
    return img


def build_table(root: Path, max_rois: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_dir = root / "csv"
    mask_dir = root / "masks"
    rows = []
    roi_rows = []
    csv_files = sorted(p for p in csv_dir.glob("*.csv") if p.name != "ALL_FOV_LOCATIONS.csv")
    if max_rois:
        csv_files = csv_files[:max_rois]
    for csv_path in csv_files:
        roi = csv_path.stem
        mask_path = mask_dir / f"{roi}.png"
        region = read_mask_region(mask_path)
        has_mask = region is not None
        df = pd.read_csv(csv_path)
        roi_region_counts: dict[str, int] = {}
        for idx, row in df.iterrows():
            x, y = centroid_from_coords(row)
            region_code = -1
            region_label = "mask_missing"
            if region is not None:
                xi = int(np.clip(round(x), 0, region.shape[1] - 1))
                yi = int(np.clip(round(y), 0, region.shape[0] - 1))
                region_code = int(region[yi, xi])
                region_label = REGION_CODE.get(region_code, f"region_{region_code}")
                roi_region_counts[region_label] = roi_region_counts.get(region_label, 0) + 1
            group = str(row.get("group", ""))
            rows.append(
                {
                    "roi": roi,
                    "object_id": f"{roi}::{idx}",
                    "x": x,
                    "y": y,
                    "raw_group": row.get("raw_group", ""),
                    "cell_label": group,
                    "cell_family": CELL_GROUP.get(group, "other_or_unknown"),
                    "manual_region_code": region_code,
                    "manual_region_label": region_label,
                    "has_region_mask": has_mask,
                    "source_csv": str(csv_path),
                    "source_mask": str(mask_path) if mask_path.exists() else "",
                }
            )
        roi_rows.append(
            {
                "roi": roi,
                "n_objects": int(len(df)),
                "has_region_mask": bool(has_mask),
                "n_region_labels_at_centroids": int(len(roi_region_counts)),
                "region_labels_at_centroids": ";".join(sorted(roi_region_counts)),
                "cell_labels": ";".join(sorted(df["group"].dropna().astype(str).unique())),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(roi_rows)


def decision(cell_table: pd.DataFrame, roi_table: pd.DataFrame) -> dict[str, object]:
    n_rois = int(cell_table["roi"].nunique()) if len(cell_table) else 0
    n_cells = int(len(cell_table))
    has_cell_classes = bool(cell_table["cell_family"].isin(["cancer_cell", "stromal_cell", "til_cell"]).any()) if len(cell_table) else False
    has_region_masks = bool(roi_table["has_region_mask"].any()) if len(roi_table) else False
    region_labels = sorted(set(cell_table["manual_region_label"].dropna().astype(str))) if len(cell_table) else []
    has_tumor_stroma_region = any(x in region_labels for x in ["Cancerous_epithelium", "Stroma", "TILs_region"])

    if n_rois >= 50 and has_cell_classes and has_region_masks and has_tumor_stroma_region:
        status = "PASS_MINIMAL_ORTHOGONAL_CELL_LEVEL_VALIDATION"
        claim = "orthogonal H&E manual region+nuclei validation layer"
    elif n_rois >= 50 and has_cell_classes and not has_region_masks:
        status = "PARTIAL_CELL_LABEL_ONLY_NEEDS_MASKS"
        claim = "manual nuclei geometry only; region masks still required"
    else:
        status = "INSUFFICIENT_FOR_POSITIVE_VALIDATION"
        claim = "candidate only"
    return {
        "dataset": "PanopTILs_manual_regions_manual_nuclei",
        "n_rois": n_rois,
        "n_objects": n_cells,
        "has_cell_classes": has_cell_classes,
        "has_region_masks": has_region_masks,
        "region_labels": ";".join(region_labels),
        "decision": status,
        "claim_level": claim,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="external_resources/panoptils_manual")
    parser.add_argument("--out-dir", default="results/snra_panoptils_manual_adapter_v1_0")
    parser.add_argument("--max-rois", type=int, default=None)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cell_table, roi_table = build_table(root, max_rois=args.max_rois)
    dec = decision(cell_table, roi_table)

    cell_table.to_csv(out_dir / "panoptils_manual_cell_region_table.tsv", sep="\t", index=False)
    roi_table.to_csv(out_dir / "panoptils_manual_roi_audit.tsv", sep="\t", index=False)
    pd.DataFrame([dec]).to_csv(out_dir / "panoptils_manual_adapter_decision.tsv", sep="\t", index=False)
    (out_dir / "panoptils_manual_adapter_decision.json").write_text(
        json.dumps(dec, indent=2), encoding="utf-8"
    )
    print(json.dumps(dec, indent=2))


if __name__ == "__main__":
    main()
