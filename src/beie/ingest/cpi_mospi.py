"""MoSPI CPI importer — loads and normalizes the official CPI snapshot.

Source: MoSPI Press Release (Annexure IV), Base 2024=100.
Snapshot: data/raw/mospi_cpi_2026.json
Provenance: data/raw/mospi_cpi_2026.provenance.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from beie.ingest.base import PROCESSED_DIR, RAW_DIR, BaseImporter, IngestionError


class CPIMoSPIImporter(BaseImporter):
    source_name = "MoSPI CPI Press Release (Annexure IV)"
    source_url = "https://mospi.gov.in/consumer-price-index"
    licence_or_terms = "Open Government Data License - India (OGDL)"

    _raw_file = RAW_DIR / "mospi_cpi_2026.json"

    def load_raw(self) -> list[dict]:
        if not self._raw_file.exists():
            raise IngestionError(
                f"[BLOCKER] CPI snapshot not found at {self._raw_file}. "
                "Download from https://mospi.gov.in and place it at the path above. "
                "BEIE will not substitute zeros or synthetic data."
            )
        with open(self._raw_file, encoding="utf-8") as fh:
            return json.load(fh)

    def normalize(self, raw: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(raw)
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df = df.sort_values("month").reset_index(drop=True)
        # enforce types
        for col in ["cpi_index", "cpi_inflation", "food_inflation", "fuel_inflation"]:
            df[col] = pd.to_numeric(df[col], errors="raise")
        df["source_name"] = self.source_name
        df["source_url"] = self.source_url
        df["retrieved_at"] = "2026-10-12T17:30:00Z"
        return df

    def validate(self, df: pd.DataFrame) -> dict[str, Any]:
        report: dict[str, Any] = {
            "source": self.source_name,
            "rows": len(df),
            "issues": [],
        }
        nulls = (
            df[["cpi_index", "cpi_inflation", "food_inflation", "fuel_inflation"]]
            .isnull()
            .sum()
            .to_dict()
        )
        if any(v > 0 for v in nulls.values()):
            report["issues"].append(f"Null values detected: {nulls}")
        # Inflation plausibility check: 0% < inflation < 20%
        for col in ["cpi_inflation", "food_inflation"]:
            out_of_range = df[~df[col].between(0.0, 20.0)]
            if not out_of_range.empty:
                report["issues"].append(
                    f"{col} out of range 0-20%: {out_of_range[col].tolist()}"
                )
        report["quality_status"] = "warning" if report["issues"] else "verified"
        return report

    def save_parquet(self, df: pd.DataFrame) -> Path:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out = PROCESSED_DIR / "cpi_series.parquet"
        df.to_parquet(out, index=False)
        return out

    def run_full(self) -> dict[str, Any]:
        result = self.run()
        df: pd.DataFrame = result["data"]
        path = self.save_parquet(df)
        result["parquet_path"] = str(path)
        return result
