"""PPAC crude basket price importer.

Source: Petroleum Planning & Analysis Cell (PPAC).
Snapshot: data/raw/ppac_crude_basket_2026.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from beie.ingest.base import PROCESSED_DIR, RAW_DIR, BaseImporter, IngestionError


class CrudePPACImporter(BaseImporter):
    source_name = "Petroleum Planning & Analysis Cell (PPAC) — Indian Crude Basket"
    source_url = "https://ppac.gov.in/prices/indian-crude-basket"
    licence_or_terms = "Ministry of Petroleum & Natural Gas — Public Data"

    _raw_file = RAW_DIR / "ppac_crude_basket_2026.csv"

    def load_raw(self) -> pd.DataFrame:
        if not self._raw_file.exists():
            raise IngestionError(
                f"[BLOCKER] PPAC crude basket snapshot not found at {self._raw_file}. "
                "Download from https://ppac.gov.in and place it at the path above."
            )
        return pd.read_csv(self._raw_file)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        for col in ["price_usd_bbl", "price_inr_bbl", "exchange_rate_inr_usd"]:
            df[col] = pd.to_numeric(df[col], errors="raise")
        df["source_name"] = self.source_name
        df["source_url"] = self.source_url
        df["retrieved_at"] = "2026-10-15T10:00:00Z"
        return df.sort_values("month").reset_index(drop=True)

    def validate(self, df: pd.DataFrame) -> dict[str, Any]:
        report: dict[str, Any] = {
            "source": self.source_name,
            "rows": len(df),
            "issues": [],
        }
        if df["price_usd_bbl"].isnull().any():
            report["issues"].append("Null crude prices detected.")
        # Plausibility: crude between $20 and $200
        if not df["price_usd_bbl"].between(20.0, 200.0).all():
            report["issues"].append("Crude price outside plausible range $20–$200/bbl.")
        report["quality_status"] = "warning" if report["issues"] else "verified"
        return report

    def save_parquet(self, df: pd.DataFrame) -> Path:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out = PROCESSED_DIR / "crude_basket.parquet"
        df.to_parquet(out, index=False)
        return out

    def run_full(self) -> dict[str, Any]:
        result = self.run()
        df: pd.DataFrame = result["data"]
        path = self.save_parquet(df)
        result["parquet_path"] = str(path)
        return result
