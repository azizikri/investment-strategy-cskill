from __future__ import annotations

import math

import numpy as np

__all__ = [
    "kelly_criterion",
    "calculate_position_size",
]


def kelly_criterion(win_rate: float, win_loss_ratio: float) -> float:
    """Compute the Half-Kelly position fraction using the Kelly Criterion.

    Wall Street standard (binary bet) Kelly sizing uses:
        f* = p - (1 - p) / b

    Where:
    - p: probability of a win (win_rate, in [0, 1])
    - b: win/loss ratio (average win magnitude / average loss magnitude), b > 0

    This function returns *Half-Kelly* for more conservative sizing:
        f_half = 0.5 * f*

    Args:
        win_rate: Probability of winning. Values outside [0, 1] are clipped.
        win_loss_ratio: Average win divided by average loss magnitude. Must be > 0.

    Returns:
        Half-Kelly fraction as a float in [0.0, 1.0]. Returns 0.0 when inputs
        are invalid or imply a non-positive edge.
    """
    if not (math.isfinite(win_rate) and math.isfinite(win_loss_ratio)):
        return 0.0

    p = float(np.clip(win_rate, 0.0, 1.0))
    b = float(win_loss_ratio)
    if b <= 0.0:
        return 0.0

    full_kelly = p - (1.0 - p) / b
    half_kelly = 0.5 * full_kelly

    if not math.isfinite(half_kelly):
        return 0.0

    return float(np.clip(half_kelly, 0.0, 1.0))


def calculate_position_size(
    portfolio_value: float,
    kelly_fraction: float,
    max_allocation: float = 0.25,
) -> float:
    """Convert a Kelly fraction into a currency position size.

    Args:
        portfolio_value: Total portfolio value in currency units.
        kelly_fraction: Fraction to allocate (e.g., output from `kelly_criterion`).
        max_allocation: Hard cap on allocation as a fraction of the portfolio.

    Returns:
        Position size in currency units (>= 0.0). Returns 0.0 for non-positive or
        non-finite inputs.
    """
    if not (math.isfinite(portfolio_value) and math.isfinite(kelly_fraction) and math.isfinite(max_allocation)):
        return 0.0

    pv = float(portfolio_value)
    if pv <= 0.0:
        return 0.0

    cap = float(max_allocation)
    if cap <= 0.0:
        return 0.0

    fraction = float(np.clip(kelly_fraction, 0.0, cap))
    return float(max(0.0, pv * fraction))
