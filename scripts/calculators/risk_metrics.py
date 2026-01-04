from __future__ import annotations

import math
from typing import Tuple

import numpy as np

__all__ = [
    "calculate_sharpe_ratio",
    "calculate_sortino_ratio",
    "calculate_max_drawdown",
    "calculate_cagr",
    "calculate_volatility",
]


TRADING_DAYS_PER_YEAR: int = 252


def _to_1d_float_array(data: list) -> np.ndarray:
    """Convert a Python list into a 1D numpy float array.

    Args:
        data: List-like container of numeric returns/values.

    Returns:
        1D numpy array of dtype float.

    Raises:
        ValueError: If values cannot be converted to floats.
    """
    try:
        arr = np.asarray(data, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Input data must be numeric and convertible to float") from exc

    return arr.reshape(-1)


def _annual_to_periodic_rate(annual_rate: float, periods_per_year: int) -> float:
    """Convert an annual effective rate into a per-period effective rate."""
    if not (math.isfinite(annual_rate) and math.isfinite(periods_per_year)):
        return 0.0

    if periods_per_year <= 0:
        return 0.0

    r = float(annual_rate)
    # If annual_rate <= -1, compounding is invalid; treat as 0 for robustness.
    if r <= -1.0:
        return 0.0

    return (1.0 + r) ** (1.0 / float(periods_per_year)) - 1.0


def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.05) -> float:
    """Calculate the annualized Sharpe ratio.

    Assumptions:
    - `returns` are *daily* simple returns.
    - `risk_free_rate` is an annual effective rate (default 5% for Indonesia context).

    Formula (standard):
        Sharpe = sqrt(N) * mean(excess_returns) / std(excess_returns)

    Where N is the number of trading periods per year (252 by default).

    Args:
        returns: List of periodic returns (floats).
        risk_free_rate: Annual risk-free rate as a decimal (e.g., 0.05 for 5%).

    Returns:
        Annualized Sharpe ratio. Returns 0.0 for insufficient data.
        Returns +inf when volatility is zero but mean excess return is positive.
    """
    r = _to_1d_float_array(returns)
    if r.size < 2:
        return 0.0

    rf_periodic = _annual_to_periodic_rate(risk_free_rate, TRADING_DAYS_PER_YEAR)
    excess = r - rf_periodic

    mean_excess = float(np.mean(excess))
    std_excess = float(np.std(excess, ddof=1))

    if not (math.isfinite(mean_excess) and math.isfinite(std_excess)):
        return 0.0

    if std_excess == 0.0:
        return float("inf") if mean_excess > 0.0 else 0.0

    return float(np.sqrt(TRADING_DAYS_PER_YEAR) * mean_excess / std_excess)


def calculate_sortino_ratio(returns: list, risk_free_rate: float = 0.05) -> float:
    """Calculate the annualized Sortino ratio.

    Assumptions:
    - `returns` are *daily* simple returns.
    - Downside risk is measured relative to the per-period risk-free rate.

    Standard definition:
        Sortino = sqrt(N) * mean(excess_returns) / downside_deviation

    Downside deviation is computed as:
        downside_deviation = sqrt(mean(min(0, excess_returns)^2))

    Args:
        returns: List of periodic returns (floats).
        risk_free_rate: Annual risk-free rate as a decimal.

    Returns:
        Annualized Sortino ratio. Returns 0.0 for insufficient data.
        Returns +inf when downside deviation is zero but mean excess return is positive.
    """
    r = _to_1d_float_array(returns)
    if r.size < 2:
        return 0.0

    rf_periodic = _annual_to_periodic_rate(risk_free_rate, TRADING_DAYS_PER_YEAR)
    excess = r - rf_periodic

    mean_excess = float(np.mean(excess))
    downside = np.minimum(0.0, excess)
    downside_dev = float(np.sqrt(np.mean(np.square(downside))))

    if not (math.isfinite(mean_excess) and math.isfinite(downside_dev)):
        return 0.0

    if downside_dev == 0.0:
        return float("inf") if mean_excess > 0.0 else 0.0

    return float(np.sqrt(TRADING_DAYS_PER_YEAR) * mean_excess / downside_dev)


def calculate_max_drawdown(values: list) -> Tuple[float, int, int]:
    """Calculate maximum drawdown from a portfolio value series.

    Max drawdown is the largest peak-to-trough decline:
        drawdown_t = (V_t / peak_t) - 1
        max_dd = abs(min(drawdown_t))

    Args:
        values: List of portfolio/equity values ordered in time.

    Returns:
        Tuple of (max_dd, peak_idx, trough_idx) where:
        - max_dd is a positive fraction in [0, +inf)
        - peak_idx is the index of the peak preceding the trough
        - trough_idx is the index of the trough

        For empty input, returns (0.0, -1, -1).
    """
    v = _to_1d_float_array(values)
    n = int(v.size)
    if n == 0:
        return 0.0, -1, -1
    if n == 1:
        return 0.0, 0, 0

    running_peak = float(v[0])
    running_peak_idx = 0

    best_dd = 0.0
    best_peak_idx = 0
    best_trough_idx = 0

    for i in range(n):
        val = float(v[i])
        if val > running_peak:
            running_peak = val
            running_peak_idx = i

        if running_peak > 0.0:
            dd = 1.0 - (val / running_peak)
        else:
            dd = 0.0

        if dd > best_dd:
            best_dd = dd
            best_peak_idx = running_peak_idx
            best_trough_idx = i

    return float(best_dd), int(best_peak_idx), int(best_trough_idx)


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate (CAGR).

    Formula:
        CAGR = (end_value / start_value) ** (1 / years) - 1

    Args:
        start_value: Starting value (must be > 0).
        end_value: Ending value (must be > 0).
        years: Duration in years (must be > 0).

    Returns:
        CAGR as a decimal (e.g., 0.12 for 12%). Returns 0.0 when inputs are invalid.
    """
    if not (math.isfinite(start_value) and math.isfinite(end_value) and math.isfinite(years)):
        return 0.0

    if start_value <= 0.0 or end_value <= 0.0 or years <= 0.0:
        return 0.0

    return float((end_value / start_value) ** (1.0 / years) - 1.0)


def calculate_volatility(returns: list) -> float:
    """Calculate annualized volatility (standard deviation) of returns.

    Assumptions:
    - `returns` are *daily* simple returns.

    Formula:
        vol = std(returns) * sqrt(N)

    Args:
        returns: List of periodic returns (floats).

    Returns:
        Annualized volatility as a decimal. Returns 0.0 for insufficient data.
    """
    r = _to_1d_float_array(returns)
    if r.size < 2:
        return 0.0

    std = float(np.std(r, ddof=1))
    if not math.isfinite(std):
        return 0.0

    return float(std * np.sqrt(TRADING_DAYS_PER_YEAR))
