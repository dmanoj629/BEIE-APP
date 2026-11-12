"""Tests for Problems We Solve registry and custom problem feasibility analyzer."""

from __future__ import annotations

from app.views.problems_we_solve import (
    PROBLEMS_REGISTRY,
    check_custom_problem_feasibility,
)


def test_registry_contains_all_four_categories():
    categories = {p["category"] for p in PROBLEMS_REGISTRY}
    assert "Household" in categories
    assert "Farmer" in categories
    assert "MSME" in categories
    assert "Researcher" in categories


def test_registry_has_required_fields():
    required_fields = [
        "id",
        "category",
        "tags",
        "name",
        "explanation",
        "affected",
        "why_it_matters",
        "tool",
        "target_page",
        "required_data",
        "methodology",
        "status",
    ]
    for p in PROBLEMS_REGISTRY:
        for field in required_fields:
            assert field in p, f"Problem {p.get('id')} missing field {field}"
        assert p["status"] in ("Operational", "Experimental", "Planned", "Unavailable")


def test_feasibility_crude_oil_query():
    res = check_custom_problem_feasibility("How will global crude oil rising affect my diesel transport cost?")
    assert res["data_available"] is True
    assert res["calculation_feasible"] is True
    assert "Energy" in res["identified_domain"]


def test_feasibility_agriculture_heat_query():
    res = check_custom_problem_feasibility("Summer heatwave is destroying my paddy rice crop in Mandya.")
    assert res["data_available"] is True
    assert res["calculation_feasible"] is True
    assert "Agriculture" in res["identified_domain"]


def test_feasibility_unmodeled_query():
    res = check_custom_problem_feasibility("How does cryptocurrency trading in Mars affect wheat prices?")
    assert res["calculation_feasible"] is False
    assert len(res["missing_evidence"]) > 0
    assert "no silent synthetic" in res["recommendation"].lower()
