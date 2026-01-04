from __future__ import annotations

import math
from typing import List

__all__ = [
    "check_allocation_drift",
    "calculate_rebalance_trades",
]


_EPS: float = 1e-12


def check_allocation_drift(current: dict, target: dict, threshold: float = 0.05) -> List[dict]:
    """Check allocation drift between current and target weights.

    Drift is measured as the absolute difference in weights (percentage points
    expressed as decimals). Example: threshold=0.05 means 5 percentage points.

    Args:
        current: Mapping of asset -> current weight (e.g., {"stocks": 0.6}).
        target: Mapping of asset -> target weight.
        threshold: Absolute weight difference that triggers a rebalance.

    Returns:
        List of dicts for assets needing rebalancing. Each dict includes:
        - asset: str
        - action: "buy" or "sell"
        - amount: float (absolute weight difference)
        - current_weight: float
        - target_weight: float
        - drift: float (current - target)

        Empty list if no assets breach the threshold.
    """
    if threshold is None or not math.isfinite(float(threshold)):
        threshold_value = 0.05
    else:
        threshold_value = float(threshold)

    assets = set(current.keys()) | set(target.keys())
    results: List[dict] = []

    for asset in sorted(assets):
        current_w = float(current.get(asset, 0.0) or 0.0)
        target_w = float(target.get(asset, 0.0) or 0.0)

        drift = current_w - target_w
        if abs(drift) + _EPS < max(threshold_value, 0.0):
            continue

        action = "sell" if drift > 0.0 else "buy"
        results.append(
            {
                "asset": asset,
                "action": action,
                "amount": float(abs(drift)),
                "current_weight": current_w,
                "target_weight": target_w,
                "drift": float(drift),
            }
        )

    results.sort(key=lambda x: abs(float(x.get("drift", 0.0))), reverse=True)
    return results


def calculate_rebalance_trades(portfolio_value: float, current: dict, target: dict) -> List[dict]:
    """Calculate rebalance trades (buy/sell) to reach target weights.

    This assumes `current` and `target` values are portfolio weights.

    Args:
        portfolio_value: Total portfolio value in currency units.
        current: Mapping of asset -> current weight.
        target: Mapping of asset -> target weight.

    Returns:
        List of dicts describing trades, each including:
        - asset: str
        - action: "buy" or "sell"
        - amount: float (currency amount to trade, absolute)
        - current_value: float
        - target_value: float
        - trade_value: float (target_value - current_value; signed)

        Empty list if portfolio_value is non-positive or no trades are needed.
    """
    if portfolio_value is None or not math.isfinite(float(portfolio_value)):
        return []

    pv = float(portfolio_value)
    if pv <= 0.0:
        return []

    assets = set(current.keys()) | set(target.keys())
    trades: List[dict] = []

    for asset in sorted(assets):
        current_w = float(current.get(asset, 0.0) or 0.0)
        target_w = float(target.get(asset, 0.0) or 0.0)

        current_value = pv * current_w
        target_value = pv * target_w
        trade_value = target_value - current_value

        if abs(trade_value) <= _EPS:
            continue

        action = "buy" if trade_value > 0.0 else "sell"
        trades.append(
            {
                "asset": asset,
                "action": action,
                "amount": float(abs(trade_value)),
                "current_value": float(current_value),
                "target_value": float(target_value),
                "trade_value": float(trade_value),
            }
        )

    trades.sort(key=lambda x: float(x.get("amount", 0.0)), reverse=True)
    return trades
