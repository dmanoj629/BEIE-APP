"""Unit tests for BEIE data contracts."""

import pytest
from pydantic import ValidationError

from beie.contracts import (
    DecisionResponse,
    ModeEnum,
    Observation,
)


def test_observation_valid():
    obs = Observation(
        indicator="CPI_HEADLINE",
        value=5.54,
        unit="% YoY",
        location="All-India",
        observed_at="2026-09",
        retrieved_at="2026-10-12T17:30:00Z",
        source_name="MoSPI Annexure IV",
        source_url="https://www.mospi.gov.in/cpi-sep-2026",
    )
    assert obs.indicator == "CPI_HEADLINE"
    assert obs.value == 5.54
    assert obs.quality_status == "verified"


def test_observation_missing_mandatory_field():
    with pytest.raises(ValidationError):
        # Missing indicator and observed_at
        Observation(value=5.54, unit="%")  # type: ignore


def test_decision_response_valid():
    resp = DecisionResponse(
        request_id="req-test-001",
        domain="energy",
        panel="citizen",
        summary="A 25% increase in crude oil is expected to increase Karnataka household living costs by 0.51 percentage points.",
        mode=ModeEnum.SCENARIO_ONLY,
        assumptions=["Crude shock: +25%", "OMC pass-through: Partial (50%)"],
        risks=["Higher transport markups may spill into perishable vegetables"],
        limitations=["Food price seasonal variations are unmodeled in this crude loop"],
    )
    assert resp.mode == ModeEnum.SCENARIO_ONLY
    assert resp.panel == "citizen"
    assert len(resp.assumptions) == 2
