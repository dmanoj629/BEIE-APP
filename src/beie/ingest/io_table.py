"""15-sector input-output matrix loader with provenance."""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from beie.ingest.base import RAW_DIR, BaseImporter, IngestionError


class IOTableImporter(BaseImporter):
    source_name = (
        "MoSPI / CSO National Accounts Supply-Use Table (15-sector aggregation)"
    )
    source_url = "https://www.mospi.gov.in/publication/supply-and-use-tables"
    licence_or_terms = "Government of India National Accounts — Fair Use Aggregation"

    _raw_file = RAW_DIR / "io_matrix_15sector.json"

    def load_raw(self) -> dict:
        if not self._raw_file.exists():
            raise IngestionError(
                f"[BLOCKER] IO matrix snapshot not found at {self._raw_file}."
            )
        with open(self._raw_file, encoding="utf-8") as fh:
            return json.load(fh)

    def normalize(self, raw: dict) -> dict[str, Any]:
        result = {
            "sectors": raw["sectors"],
            "crude_cost_share_ac": np.array(raw["crude_cost_share_ac"], dtype=float),
            "cpi_mapping_weights": np.array(raw["cpi_mapping_weights"], dtype=float),
            "n_sectors": len(raw["sectors"]),
        }
        if "io_matrix_A" in raw:
            result["io_matrix_A"] = np.array(raw["io_matrix_A"], dtype=float)
        return result

    def validate(self, data: dict) -> dict[str, Any]:
        report: dict[str, Any] = {"source": self.source_name, "issues": []}
        ac = data["crude_cost_share_ac"]
        if np.any(ac < 0) or np.any(ac > 1):
            report["issues"].append("Crude cost shares outside [0, 1].")
        weights = data["cpi_mapping_weights"]
        total = float(weights.sum())
        if not (0.95 <= total <= 1.05):
            report["issues"].append(
                f"CPI mapping weights sum to {total:.4f}, expected ~1.0."
            )
        if "io_matrix_A" in data:
            A = data["io_matrix_A"]
            if A.shape != (data["n_sectors"], data["n_sectors"]):
                report["issues"].append(f"IO matrix A has invalid dimensions {A.shape}, expected ({data['n_sectors']}, {data['n_sectors']}).")
            if np.any(A < 0):
                report["issues"].append("IO matrix A contains negative coefficients.")
            col_sums = A.sum(axis=0)
            if np.any(col_sums >= 1.0):
                report["issues"].append("Hawkins-Simon violation: column sums of matrix A exceed 1.0.")
        report["quality_status"] = "warning" if report["issues"] else "verified"
        return report
