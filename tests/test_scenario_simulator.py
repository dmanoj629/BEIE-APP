"""Tests for Universal Economic Scenario Simulator and parameter extraction."""

from __future__ import annotations

from app.views.scenario_simulator import extract_scenario_parameters


def test_extract_crude_percentage():
    params = extract_scenario_parameters("What if crude oil jumps 35% next month?")
    assert params.get("crude") == 35.0


def test_extract_multi_shock_parameters():
    text = "Suppose diesel rises 15%, electricity increases 8%, and freight increases 12%."
    params = extract_scenario_parameters(text)
    assert params.get("diesel") == 15.0
    assert params.get("power") == 8.0
    assert params.get("freight") == 12.0


def test_extract_repo_bps():
    text = "What if RBI hikes repo rate by 50 bps?"
    params = extract_scenario_parameters(text)
    assert params.get("repo_bps") == 50.0


def test_extract_generic_percentage():
    params = extract_scenario_parameters("Crude spike of 20%")
    assert params.get("crude") == 20.0
