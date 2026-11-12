"""Provenance audit tests — guarantees no empty hash or corrupted data sidecars."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from beie.ingest.base import RAW_DIR

DATA_PROVENANCE_PAIRS = [
    ("cpi_weights_karnataka.json", "cpi_weights_karnataka.provenance.json"),
    ("io_matrix_15sector.json", "io_matrix_15sector.provenance.json"),
    ("mospi_cpi_2026.json", "mospi_cpi_2026.provenance.json"),
    ("ppac_crude_basket_2026.csv", "ppac_crude_basket_2026.provenance.json"),
    ("ppac_pump_prices_2026.csv", "ppac_pump_prices_2026.provenance.json"),
]

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_provenance_hashes_match_actual_files():
    """Verify that every recorded sha256 matches the actual byte hash of the file."""
    for dname, pname in DATA_PROVENANCE_PAIRS:
        data_file = RAW_DIR / dname
        prov_file = RAW_DIR / pname

        assert data_file.exists(), f"Data file missing: {dname}"
        assert prov_file.exists(), f"Provenance file missing: {pname}"

        content = data_file.read_bytes()
        actual_hash = hashlib.sha256(content).hexdigest()

        with open(prov_file, encoding="utf-8") as f:
            prov = json.load(f)

        recorded_hash = prov.get("sha256")
        assert recorded_hash != EMPTY_SHA256, (
            f"Provenance {pname} contains empty-file SHA256!"
        )
        assert recorded_hash == actual_hash, (
            f"Hash mismatch in {pname}: recorded {recorded_hash} vs actual {actual_hash}"
        )


def test_provenance_has_required_metadata_fields():
    """Every provenance sidecar must have source_name, source_url, retrieved_at, licence_or_terms."""
    for _, pname in DATA_PROVENANCE_PAIRS:
        prov_file = RAW_DIR / pname
        with open(prov_file, encoding="utf-8") as f:
            prov = json.load(f)

        assert "source_name" in prov and len(prov["source_name"]) > 0
        assert "source_url" in prov and prov["source_url"].startswith("http")
        assert "retrieved_at" in prov
        assert "licence_or_terms" in prov
