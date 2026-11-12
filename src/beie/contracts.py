"""Data and response contracts for the Bharat Economic Intelligence Engine (BEIE).

Strictly enforces Section 3 and Section 6.4 of the BEIE Blueprint:
- Provenance on every observation
- Explicit modes: data_driven, scenario_only, demo, limited
- Separation of observations, assumptions, inferences, and uncertainties
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ModeEnum(str, Enum):
    DATA_DRIVEN = "data_driven"
    SCENARIO_ONLY = "scenario_only"
    DEMO = "demo"
    LIMITED = "limited"


class Observation(BaseModel):
    """A single factual observation sourced from verified economic data."""

    indicator: str = Field(
        ..., description="Name of the economic indicator (e.g. CPI_HEADLINE)"
    )
    value: float = Field(..., description="Numeric value of the observation")
    unit: str = Field(
        ..., description="Measurement unit (e.g. '% YoY', '₹/litre', 'USD/bbl')"
    )
    location: str = Field(
        ..., description="Geographic location (e.g. 'All-India', 'Karnataka', 'Delhi')"
    )
    entity: str | None = Field(
        None, description="Optional reporting entity (e.g. 'PPAC', 'MoSPI')"
    )
    sector: str | None = Field(None, description="Economic sector if applicable")
    category: str | None = Field(None, description="Category or subgroup")
    observed_at: str = Field(
        ..., description="ISO date or period of observation (e.g. '2026-09')"
    )
    retrieved_at: str = Field(
        ..., description="ISO timestamp when observation was fetched/snapshotted"
    )
    source_name: str = Field(
        ..., description="Official publisher name (e.g. 'MoSPI Annexure IV')"
    )
    source_url: str = Field(..., description="Official URL or document identifier")
    licence_or_terms: str = Field(
        "Open Government Data License - India (OGDL)", description="Licence or terms"
    )
    quality_status: str = Field(
        "verified", description="'verified', 'provisional', 'warning', 'missing'"
    )
    transformation_version: str = Field(
        "1.0.0", description="Version of normalization pipeline"
    )


class Evidence(BaseModel):
    """Citation and provenance record for supporting evidence."""

    source_name: str
    source_url: str
    retrieved_at: str
    licence_or_terms: str
    description: str
    sha256: str | None = None


class DecisionRequest(BaseModel):
    """Unified request schema dispatched to BEIE Decision Service."""

    request_id: str
    domain: str = Field(
        ...,
        description="Domain: 'energy', 'agriculture', 'finance', 'purchase', 'markets'",
    )
    panel: str = Field(..., description="'citizen' or 'business'")
    query: str = Field(..., description="User query or trigger question")
    geography: str = Field("Karnataka", description="Primary target region")
    user_profile: dict[str, Any] = Field(
        default_factory=dict, description="Anonymized user profile from onboarding"
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain/scenario parameters (e.g. crude_delta_pct, fuel_policy)",
    )


class DecisionResponse(BaseModel):
    """Binding response contract as mandated by BEIE Blueprint Page 6."""

    request_id: str
    domain: str
    panel: str
    summary: str = Field(
        ..., description="Direct, concise plain-language headline answer"
    )
    observations: list[Observation] = Field(
        default_factory=list, description="Sourced facts with provenance"
    )
    options: list[dict[str, Any]] = Field(
        default_factory=list, description="Comparable alternatives and calculations"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Explicit user or model assumptions"
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Downside risks, second-round effects, and warnings",
    )
    uncertainty: dict[str, Any] = Field(
        default_factory=dict,
        description="Monte Carlo bands (P10, P50, P90, std, draws)",
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="Formal citations, URLs, dates"
    )
    validation: dict[str, Any] = Field(
        default_factory=dict,
        description="Baseline comparison, backtest errors, MAE vs naive",
    )
    mode: ModeEnum = Field(..., description="Operating mode badge")
    model_version: str = Field(
        "BEIE-v1.0.0", description="Version tag of the active engine"
    )
    limitations: list[str] = Field(
        default_factory=list, description="Explicit system limitations and caveats"
    )
    run_record: dict[str, Any] | None = Field(
        None, description="Auditable run metadata (seed, draws, timestamp, hash)"
    )
