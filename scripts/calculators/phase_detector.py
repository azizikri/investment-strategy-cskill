from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "detect_phase",
    "get_allocation_target",
]


_PHASE_1_TARGET: Dict[str, float] = {
    "ef": 0.80,
    "stocks": 0.10,
    "crypto": 0.10,
}

_PHASE_2_TARGET: Dict[str, float] = {
    "ef": 0.20,
    "stocks": 0.50,
    "crypto": 0.20,
    "bonds": 0.10,
}


def detect_phase(ef_balance: float, ef_target: float) -> int:
    """Detect investment phase based on Emergency Fund (EF) progress.

    Phase definitions:
    - Phase 1: EF balance is below 100% of EF target (EF < target)
    - Phase 2: EF balance is at or above 100% of EF target (EF >= target)

    Args:
        ef_balance: Current emergency fund balance.
        ef_target: Target emergency fund balance.

    Returns:
        1 or 2.

    Notes:
        If `ef_target` is non-positive or non-finite, Phase 2 is returned because
        the target is treated as already satisfied.
    """
    if not (math.isfinite(ef_balance) and math.isfinite(ef_target)):
        return 2

    if ef_target <= 0.0:
        return 2

    return 1 if ef_balance < ef_target else 2


def get_allocation_target(phase: int) -> dict:
    """Return recommended allocation weights for the given phase.

    Phase 1 allocation (conservative, EF-building):
    - 80% EF
    - 10% stocks
    - 10% crypto

    Phase 2 allocation (more aggressive investing):
    - 20% EF maintenance
    - 50% stocks
    - 20% crypto
    - 10% bonds

    Args:
        phase: The phase number, expected to be 1 or 2.

    Returns:
        Dict mapping asset class to allocation weight (sums to ~1.0).

    Raises:
        ValueError: If phase is not 1 or 2.
    """
    if phase == 1:
        return dict(_PHASE_1_TARGET)
    if phase == 2:
        return dict(_PHASE_2_TARGET)

    raise ValueError("phase must be 1 or 2")
