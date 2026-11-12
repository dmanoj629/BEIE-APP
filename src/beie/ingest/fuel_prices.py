"""PPAC retail fuel pump prices importer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from beie.ingest.base import PROCESSED_DIR, RAW_DIR, BaseImporter, IngestionError


class FuelPricesImporter(BaseImporter):
    source_name = "PPAC / IOCL Retail Pump Price Notifications"
    source_url = "https://ppac.gov.in/retail-selling-price-petrol-diesel"
    licence_or_terms = "Ministry of Petroleum & Natural Gas — Public Data"

    _raw_file = RAW_DIR / "ppac_pump_prices_2026.csv"

    def load_raw(self) -> pd.DataFrame:
        if not self._raw_file.exists():
            raise IngestionError(
                f"[BLOCKER] PPAC pump price snapshot not found at {self._raw_file}."
            )
        return pd.read_csv(self._raw_file)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        df["effective_date"] = pd.to_datetime(df["effective_date"])
        df["price_inr_per_litre"] = pd.to_numeric(
            df["price_inr_per_litre"], errors="raise"
        )
        df["tax_share_pct"] = pd.to_numeric(df["tax_share_pct"], errors="raise")
        df["source_name"] = self.source_name
        df["source_url"] = self.source_url
        df["retrieved_at"] = "2026-10-15T10:00:00Z"
        return df.sort_values("effective_date").reset_index(drop=True)

    def validate(self, df: pd.DataFrame) -> dict[str, Any]:
        report: dict[str, Any] = {
            "source": self.source_name,
            "rows": len(df),
            "issues": [],
        }
        if df["price_inr_per_litre"].isnull().any():
            report["issues"].append("Null prices detected.")
        if not df["price_inr_per_litre"].between(60.0, 200.0).all():
            report["issues"].append(
                "Fuel price outside plausible range ₹60–₹200/litre."
            )
        report["quality_status"] = "warning" if report["issues"] else "verified"
        return report

    def save_parquet(self, df: pd.DataFrame) -> Path:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out = PROCESSED_DIR / "pump_prices.parquet"
        df.to_parquet(out, index=False)
        return out

    def run_full(self) -> dict[str, Any]:
        result = self.run()
        path = self.save_parquet(result["data"])
        result["parquet_path"] = str(path)
        return result
