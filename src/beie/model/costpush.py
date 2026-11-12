"""Leontief cost-push price transmission model.

Equation (Blueprint §5):
    Δp = (I - Aᵀ)⁻¹ · a_c · Δc

where:
  A      = domestic I-O coefficient matrix (n×n), sectors as rows
  a_c    = direct crude/energy cost share vector (n,)
  Δc     = fractional crude price shock (e.g. 0.25 for +25%)
  Δp     = sectoral price change vector (n,)
"""

from __future__ import annotations

import numpy as np


def compute_leontief_price_impact(
    A: np.ndarray,
    ac: np.ndarray,
    delta_c: float,
) -> np.ndarray:
    """Return sectoral price change vector Δp from a crude shock.

    Parameters
    ----------
    A : (n, n) domestic input-output coefficient matrix.
    ac : (n,) direct crude cost share per sector.
    delta_c : fractional crude shock (0.25 → +25%).

    Returns
    -------
    delta_p : (n,) sectoral fractional price change.
    """
    n = A.shape[0]
    if A.shape != (n, n):
        raise ValueError("A must be a square matrix.")
    if ac.shape[0] != n:
        raise ValueError("ac must have the same length as A's dimension.")

    I = np.eye(n)
    # (I - A^T)^-1 · ac · Δc
    multiplier_matrix = np.linalg.inv(I - A.T)
    delta_p = multiplier_matrix @ (ac * delta_c)
    return delta_p


def build_diagonal_io(ac: np.ndarray) -> np.ndarray:
    """Build a simple diagonal A matrix where sectors only use their own crude share.

    Used as a conservative lower-bound approximation when a full supply-use
    matrix is unavailable.
    """
    return np.diag(ac * 0.5)  # half of direct crude share recycled as own intermediate


def cpi_impact_from_sectoral(
    delta_p: np.ndarray,
    cpi_weights: np.ndarray,
) -> float:
    """Aggregate sectoral price changes into a headline CPI impact (percentage points).

    Parameters
    ----------
    delta_p : (n,) fractional sectoral price changes.
    cpi_weights : (n,) CPI expenditure weight for each sector (must sum to ~1.0).

    Returns
    -------
    cpi_delta_pp : Headline CPI change in percentage points.
    """
    return float(np.dot(cpi_weights, delta_p) * 100.0)
