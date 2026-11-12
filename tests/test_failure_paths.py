"""Failure path tests — missing data files, honest limited mode, no silent fallback."""

import pytest

from beie.contracts import DecisionRequest, ModeEnum
from beie.ingest.base import IngestionError
from beie.ingest.cpi_mospi import CPIMoSPIImporter
from beie.ingest.crude_ppac import CrudePPACImporter
from beie.service import analyze_decision


def test_missing_cpi_file_raises_ingestion_error(tmp_path, monkeypatch):
    """If CPI snapshot is not found, IngestionError must be raised (never silent zeros)."""
    importer = CPIMoSPIImporter()
    monkeypatch.setattr(importer, "_raw_file", tmp_path / "nonexistent.json")
    with pytest.raises(IngestionError) as exc_info:
        importer.load_raw()
    assert "BLOCKER" in str(exc_info.value)
    # The error message must NOT silently promise synthetic data — it should block and explain
    error_msg = str(exc_info.value)
    assert (
        "not substitute" in error_msg
        or "BEIE will not" in error_msg
        or "Download" in error_msg
    )


def test_missing_crude_file_raises_ingestion_error(tmp_path, monkeypatch):
    importer = CrudePPACImporter()
    monkeypatch.setattr(importer, "_raw_file", tmp_path / "nonexistent.csv")
    with pytest.raises(IngestionError) as exc_info:
        importer.load_raw()
    assert "BLOCKER" in str(exc_info.value)


def test_unknown_domain_returns_limited_mode():
    req = DecisionRequest(
        request_id="test-limited-001",
        domain="unknown_future_domain",
        panel="citizen",
        query="What is the impact?",
    )
    resp = analyze_decision(req)
    assert resp.mode == ModeEnum.LIMITED
    assert len(resp.limitations) > 0
    assert resp.observations == []
    assert resp.uncertainty == {}


def test_passthrough_zero_policy_gives_zero_pump_delta():
    from beie.model.passthrough import FuelPolicy, compute_pump_delta

    result = compute_pump_delta(
        crude_delta_pct=0.50,
        base_diesel_price=96.45,
        base_petrol_price=109.29,
        policy=FuelPolicy.HELD,
    )
    assert result["diesel_delta"] == 0.0
    assert result["petrol_delta"] == 0.0
