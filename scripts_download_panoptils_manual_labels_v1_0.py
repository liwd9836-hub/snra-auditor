#!/usr/bin/env python
"""Download PanopTILs manual-label resources needed by SNRA.

The Google Drive folder contains RGB images, visualization images, masks and
CSV polygon labels.  For SNRA validation we only need the manual label layer:
CSV annotations and mask PNGs.  This script uses gdown's folder listing API,
then downloads selected file classes one by one so a single inaccessible Drive
file does not abort the whole transfer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


PANOPTILS_MANUAL_FOLDER = (
    "https://drive.google.com/drive/folders/"
    "17HvYYPkBOyeexXetxih5q8KxJUlt6aRT?usp=sharing"
)


def _require_gdown():
    try:
        import gdown  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Install gdown first: python -m pip install gdown") from exc
    return gdown


def list_drive_folder(out_dir: Path) -> pd.DataFrame:
    gdown = _require_gdown()
    files = gdown.download_folder(
        url=PANOPTILS_MANUAL_FOLDER,
        output=str(out_dir),
        skip_download=True,
        quiet=True,
        use_cookies=True,
    )
    rows = [
        {"id": f.id, "path": str(f.path), "local_path": str(f.local_path)}
        for f in files
    ]
    listing = pd.DataFrame(rows)
    listing_path = out_dir / "panoptils_gdrive_listing.tsv"
    listing.to_csv(listing_path, sep="\t", index=False)
    return listing


def existing_csv_basenames(out_dir: Path) -> set[str]:
    csv_dir = out_dir / "csv"
    if not csv_dir.exists():
        return set()
    return {p.stem for p in csv_dir.glob("*.csv") if p.name != "ALL_FOV_LOCATIONS.csv"}


def wanted_rows(listing: pd.DataFrame, mode: str, out_dir: Path) -> pd.DataFrame:
    path = listing["path"].astype(str)
    if mode == "csv":
        return listing[path.str.startswith("csv\\")].copy()
    if mode == "masks_for_existing_csv":
        basenames = existing_csv_basenames(out_dir)
        is_mask = path.str.startswith("masks\\")
        stem = path.map(lambda x: Path(str(x)).stem)
        return listing[is_mask & stem.isin(basenames)].copy()
    if mode == "csv_and_masks":
        return listing[path.str.startswith("csv\\") | path.str.startswith("masks\\")].copy()
    raise ValueError(f"Unknown mode: {mode}")


def download_rows(rows: pd.DataFrame, out_dir: Path, max_files: int | None = None) -> pd.DataFrame:
    gdown = _require_gdown()
    records = []
    iterable: Iterable[tuple[int, pd.Series]] = rows.iterrows()
    for i, (_, row) in enumerate(iterable, start=1):
        if max_files is not None and i > max_files:
            break
        rel_path = Path(str(row["path"]))
        target = out_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size > 0:
            records.append(
                {
                    "path": str(row["path"]),
                    "id": row["id"],
                    "status": "exists",
                    "bytes": target.stat().st_size,
                    "error": "",
                }
            )
            continue
        try:
            result = gdown.download(id=str(row["id"]), output=str(target), quiet=True, use_cookies=True)
            ok = result is not None and target.exists() and target.stat().st_size > 0
            if not ok:
                ok = download_googleusercontent_fallback(str(row["id"]), target)
            records.append(
                {
                    "path": str(row["path"]),
                    "id": row["id"],
                    "status": "downloaded" if ok else "failed",
                    "bytes": target.stat().st_size if target.exists() else 0,
                    "error": "" if ok else "gdown returned no output",
                }
            )
        except Exception as exc:  # noqa: BLE001 - record and continue
            fallback_ok = download_googleusercontent_fallback(str(row["id"]), target)
            records.append(
                {
                    "path": str(row["path"]),
                    "id": row["id"],
                    "status": "downloaded_fallback" if fallback_ok else "failed",
                    "bytes": target.stat().st_size if target.exists() else 0,
                    "error": "" if fallback_ok else str(exc),
                }
            )
    return pd.DataFrame(records)


def download_googleusercontent_fallback(file_id: str, target: Path) -> bool:
    """Fallback for public Drive files that gdown cannot resolve."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        with requests.get(url, stream=True, timeout=120, allow_redirects=True) as response:
            response.raise_for_status()
            ctype = response.headers.get("Content-Type", "")
            if "text/html" in ctype.lower():
                return False
            tmp = target.with_suffix(target.suffix + ".part")
            with tmp.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 512):
                    if chunk:
                        handle.write(chunk)
            if tmp.stat().st_size == 0:
                tmp.unlink(missing_ok=True)
                return False
            tmp.replace(target)
            return True
    except Exception:
        return False


def summarize(out_dir: Path, listing: pd.DataFrame, transfer: pd.DataFrame) -> dict[str, object]:
    files = list(out_dir.rglob("*"))
    csv_count = len(list((out_dir / "csv").glob("*.csv"))) if (out_dir / "csv").exists() else 0
    mask_count = len(list((out_dir / "masks").glob("*.png"))) if (out_dir / "masks").exists() else 0
    total_bytes = sum(p.stat().st_size for p in files if p.is_file())
    return {
        "folder_url": PANOPTILS_MANUAL_FOLDER,
        "listed_files": int(len(listing)),
        "listed_csv": int(listing["path"].astype(str).str.startswith("csv\\").sum()),
        "listed_masks": int(listing["path"].astype(str).str.startswith("masks\\").sum()),
        "local_csv": int(csv_count),
        "local_masks": int(mask_count),
        "transfer_rows": int(len(transfer)),
        "transfer_failed": int((transfer["status"] == "failed").sum()) if len(transfer) else 0,
        "local_total_mb": round(total_bytes / 1024 / 1024, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="external_resources/panoptils_manual")
    parser.add_argument(
        "--mode",
        choices=["csv", "masks_for_existing_csv", "csv_and_masks"],
        default="csv",
    )
    parser.add_argument("--max-files", type=int, default=None)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    listing = list_drive_folder(out_dir)
    rows = wanted_rows(listing, args.mode, out_dir)
    transfer = download_rows(rows, out_dir, max_files=args.max_files)

    transfer_path = out_dir / f"panoptils_transfer_{args.mode}.tsv"
    transfer.to_csv(transfer_path, sep="\t", index=False)

    summary = summarize(out_dir, listing, transfer)
    summary_path = out_dir / f"panoptils_download_summary_{args.mode}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
