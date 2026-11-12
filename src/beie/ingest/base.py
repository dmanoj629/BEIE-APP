"""Data ingestion base contract and provenance recorder."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


class IngestionError(Exception):
    """Raised when a required data source is unavailable or fails validation."""


class BaseImporter(ABC):
    """Abstract contract every BEIE importer must satisfy.

    Rules (Blueprint §4):
    - Every run records source_name, source_url, retrieved_at, sha256.
    - Missing data raises IngestionError; never returns zeros silently.
    - Provenance sidecar is written alongside every raw snapshot.
    """

    source_name: str
    source_url: str
    licence_or_terms: str = "Open Government Data License - India (OGDL)"

    @abstractmethod
    def load_raw(self) -> Any:
        """Load data from local snapshot; raise IngestionError if missing."""

    @abstractmethod
    def normalize(self, raw: Any) -> Any:
        """Return normalized, typed Python structure."""

    @abstractmethod
    def validate(self, normalized: Any) -> dict[str, Any]:
        """Return quality report dict; raise IngestionError on critical failure."""

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    def run(self) -> dict[str, Any]:
        """Full ingestion pipeline: load -> normalize -> validate -> quality report."""
        raw = self.load_raw()
        normalized = self.normalize(raw)
        report = self.validate(normalized)
        return {"data": normalized, "quality_report": report}

    @staticmethod
    def sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def now_utc() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def write_provenance(path: Path, meta: dict[str, Any]) -> None:
        prov_path = path.with_suffix(".provenance.json")
        prov_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
