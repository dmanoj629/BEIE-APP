"""Tests for intelligent onboarding context extraction (Blueprint §5D)."""

from __future__ import annotations

from app.components.onboarding import extract_context_from_text


def test_extract_coconut_oil_mfg():
    text = (
        "I operate a small coconut oil manufacturing business in Mysuru. "
        "I purchase coconuts from local farmers, use electricity for processing, "
        "and transport finished oil to local shops."
    )
    result = extract_context_from_text(text)
    stated = result["stated"]
    inferred = result["inferred"]

    assert "product" in stated
    assert "coconut" in stated["product"].lower()
    assert stated.get("energy_dependency") == "Electricity"
    assert "transportation_dependency" in stated
    assert stated.get("region") == "Mysuru"
    assert inferred.get("tariff_sensitivity") == "High"


def test_extract_empty_string():
    result = extract_context_from_text("")
    assert result["stated"] == {}
    assert result["inferred"] == {}


def test_extract_dairy_farmer():
    text = "We run a dairy farm in Hassan with diesel backup generator."
    result = extract_context_from_text(text)
    stated = result["stated"]
    assert "dairy" in stated.get("product", "").lower()
    assert stated.get("region") == "Hassan"
    assert stated.get("fuel_dependency") == "Diesel"
