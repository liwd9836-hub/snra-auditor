"""SNRA: Spatial Niche Robustness Auditor.

Lightweight first implementation for audit-first spatial niche robustness.
The package intentionally avoids heavy graph/deep-learning dependencies;
publication figure generation uses Matplotlib from the declared runtime set.
"""

from .audit import AuditConfig, run_audit
from .contract import SpatialDataset, validate_dataset

__version__ = "0.1.0"

__all__ = ["__version__", "AuditConfig", "SpatialDataset", "validate_dataset", "run_audit"]
