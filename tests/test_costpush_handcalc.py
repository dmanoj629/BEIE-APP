"""Hand-checked Leontief cost-push tests (2-sector toy example)."""

import numpy as np
import pytest

from beie.model.costpush import compute_leontief_price_impact, cpi_impact_from_sectoral


def test_zero_shock_gives_zero_delta():
    A = np.array([[0.1, 0.2], [0.3, 0.1]])
    ac = np.array([0.4, 0.2])
    delta_p = compute_leontief_price_impact(A, ac, 0.0)
    np.testing.assert_allclose(delta_p, [0.0, 0.0], atol=1e-10)


def test_two_sector_hand_calculation():
    """Hand-verified 2-sector test.
    A = [[0.0, 0.0], [0.0, 0.0]] (no inter-industry linkage)
    ac = [0.5, 0.2]
    delta_c = 0.10 (+10%)
    Expected: Δp = (I - 0)^-1 · ac · 0.10 = ac * 0.10 = [0.05, 0.02]
    """
    A = np.zeros((2, 2))
    ac = np.array([0.5, 0.2])
    delta_c = 0.10
    delta_p = compute_leontief_price_impact(A, ac, delta_c)
    np.testing.assert_allclose(delta_p, [0.05, 0.02], atol=1e-10)


def test_cpi_aggregation_hand_checked():
    """CPI impact from sectoral: Δp=[0.05, 0.02], w=[0.6, 0.4] → (0.05*0.6+0.02*0.4)*100 = 3.8pp"""
    delta_p = np.array([0.05, 0.02])
    cpi_w = np.array([0.6, 0.4])
    result = cpi_impact_from_sectoral(delta_p, cpi_w)
    assert abs(result - 3.8) < 1e-8


def test_nonsquare_matrix_raises():
    A = np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])  # 2x3
    ac = np.array([0.1, 0.2])
    with pytest.raises((ValueError, np.linalg.LinAlgError)):
        compute_leontief_price_impact(A, ac, 0.1)
