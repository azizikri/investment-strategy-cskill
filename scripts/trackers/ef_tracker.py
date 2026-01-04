"""Emergency Fund tracker for Phase 1/2 progress monitoring."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

__all__ = [
    "EmergencyFundTracker",
]


DATA_DIR = Path(__file__).parent.parent.parent / "data"
EF_FILE = DATA_DIR / "ef_progress.json"


class EmergencyFundTracker:
    """Tracks Emergency Fund progress toward 6-month target."""

    DEFAULT_TARGET_MONTHS = 6
    DEFAULT_MONTHLY_EXPENSES = 6_000_000

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path) if data_path else EF_FILE
        self.target_months: int = self.DEFAULT_TARGET_MONTHS
        self.monthly_expenses: float = self.DEFAULT_MONTHLY_EXPENSES
        self.current_balance: float = 0.0
        self.history: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load EF data from disk."""
        if not self.data_path.exists():
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            self.target_months = data.get("target_months", self.DEFAULT_TARGET_MONTHS)
            self.monthly_expenses = data.get("monthly_expenses", self.DEFAULT_MONTHLY_EXPENSES)
            self.current_balance = data.get("current_balance", 0.0)
            self.history = data.get("history", [])
        except (json.JSONDecodeError, KeyError):
            pass

    def save(self) -> None:
        """Persist EF data to disk."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "target_amount": self.target_amount,
            "target_months": self.target_months,
            "monthly_expenses": self.monthly_expenses,
            "current_balance": self.current_balance,
            "months_covered": self.months_covered,
            "progress_percent": self.progress_percent,
            "phase": self.current_phase,
            "last_updated": datetime.now().isoformat(),
            "history": self.history,
        }

        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @property
    def target_amount(self) -> float:
        """Target emergency fund amount."""
        return self.target_months * self.monthly_expenses

    @property
    def months_covered(self) -> float:
        """Number of months covered by current balance."""
        if self.monthly_expenses <= 0:
            return 0.0
        return self.current_balance / self.monthly_expenses

    @property
    def progress_percent(self) -> float:
        """Progress toward target as percentage."""
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, (self.current_balance / self.target_amount) * 100)

    @property
    def current_phase(self) -> int:
        """Current investment phase (1 = building EF, 2 = wealth accumulation)."""
        return 2 if self.months_covered >= self.target_months else 1

    @property
    def is_complete(self) -> bool:
        """Whether emergency fund target is met."""
        return self.current_balance >= self.target_amount

    @property
    def amount_remaining(self) -> float:
        """Amount still needed to reach target."""
        return max(0.0, self.target_amount - self.current_balance)

    def configure(
        self,
        target_months: int | None = None,
        monthly_expenses: float | None = None,
    ) -> None:
        """Update EF configuration."""
        if target_months is not None:
            self.target_months = int(target_months)
        if monthly_expenses is not None:
            self.monthly_expenses = float(monthly_expenses)
        self.save()

    def update_balance(self, new_balance: float, add_to_history: bool = True) -> None:
        """Update current emergency fund balance."""
        self.current_balance = float(new_balance)

        if add_to_history:
            self.history.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "balance": self.current_balance,
                "months_covered": round(self.months_covered, 2),
            })

        self.save()

    def add_contribution(self, amount: float) -> None:
        """Add contribution to emergency fund."""
        self.update_balance(self.current_balance + float(amount))

    def withdraw(self, amount: float) -> bool:
        """Withdraw from emergency fund."""
        if amount > self.current_balance:
            return False

        self.update_balance(self.current_balance - float(amount))
        return True

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive EF status."""
        return {
            "current_balance": self.current_balance,
            "target_amount": self.target_amount,
            "target_months": self.target_months,
            "monthly_expenses": self.monthly_expenses,
            "months_covered": round(self.months_covered, 2),
            "progress_percent": round(self.progress_percent, 1),
            "amount_remaining": self.amount_remaining,
            "current_phase": self.current_phase,
            "is_complete": self.is_complete,
            "phase_label": "Foundation Building" if self.current_phase == 1 else "Wealth Accumulation",
        }

    def get_monthly_contribution_needed(self, months_to_goal: int = 12) -> float:
        """Calculate monthly contribution needed to reach goal."""
        if months_to_goal <= 0:
            return 0.0
        return self.amount_remaining / months_to_goal

    def get_history_summary(self) -> list[dict[str, Any]]:
        """Get history entries."""
        return self.history.copy()

    def estimate_completion_date(self, monthly_contribution: float) -> str | None:
        """Estimate when EF will be complete at given contribution rate."""
        if monthly_contribution <= 0 or self.is_complete:
            return None

        months_needed = self.amount_remaining / monthly_contribution
        from datetime import timedelta

        completion = datetime.now() + timedelta(days=months_needed * 30)
        return completion.strftime("%Y-%m")

    def get_phase_allocation(self) -> dict[str, float]:
        """Get recommended allocation percentages based on current phase."""
        if self.current_phase == 1:
            return {
                "emergency_fund": 80.0,
                "investments": 10.0,
                "crypto": 10.0,
            }
        return {
            "emergency_fund": 20.0,
            "idx_stocks": 30.0,
            "us_stocks": 30.0,
            "crypto": 20.0,
        }
