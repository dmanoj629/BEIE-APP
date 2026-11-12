"""Backtest coverage test — 2022 and 2026 oil shock episodes."""

from beie.evaluation.backtest import run_backtest


def test_backtest_runs_without_error():
    result = run_backtest()
    assert "episodes" in result
    assert len(result["episodes"]) == 2


def test_backtest_reports_coverage():
    result = run_backtest()
    assert 0.0 <= result["coverage_pct"] <= 100.0


def test_backtest_has_honest_disclaimer():
    result = run_backtest()
    claim = result["accuracy_claim"]
    assert any(keyword in claim for keyword in ["BACKTEST", "coverage", "✅", "⚠️"])


def test_backtest_episodes_have_required_fields():
    result = run_backtest()
    required = [
        "episode",
        "realized_cpi_pp",
        "mc_p10",
        "mc_p50",
        "mc_p90",
        "mc_in_band",
        "source",
    ]
    for ep in result["episodes"]:
        for field in required:
            assert field in ep, (
                f"Missing field '{field}' in episode: {ep.get('episode')}"
            )
