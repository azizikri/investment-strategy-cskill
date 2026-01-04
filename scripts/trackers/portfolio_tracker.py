"""Portfolio tracker for managing positions with live price updates."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

__all__ = [
    "PortfolioTracker",
    "Position",
]


DATA_DIR = Path(__file__).parent.parent.parent / "data"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"


class Position:
    """Represents a single portfolio position."""

    def __init__(
        self,
        ticker: str,
        platform: str,
        quantity: float,
        avg_price: float,
        currency: str = "IDR",
        position_type: str = "stock",
        is_emergency_fund: bool = False,
        name: str | None = None,
        purchase_date: str | None = None,
        position_id: str | None = None,
    ):
        self.id = position_id or f"POS-{uuid.uuid4().hex[:8].upper()}"
        self.ticker = ticker.upper().strip()
        self.platform = platform.lower().strip()
        self.quantity = float(quantity)
        self.avg_price = float(avg_price)
        self.currency = currency.upper().strip()
        self.type = position_type.lower().strip()
        self.is_emergency_fund = bool(is_emergency_fund)
        self.name = name or ticker
        self.purchase_date = purchase_date or datetime.now().strftime("%Y-%m-%d")
        self.last_price: float | None = None
        self.last_updated: str | None = None

    @property
    def cost_basis(self) -> float:
        """Total cost of position."""
        return self.quantity * self.avg_price

    @property
    def current_value(self) -> float | None:
        """Current market value (None if no live price)."""
        if self.last_price is None:
            return None
        return self.quantity * self.last_price

    @property
    def unrealized_pnl(self) -> float | None:
        """Unrealized profit/loss (None if no live price)."""
        if self.current_value is None:
            return None
        return self.current_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self) -> float | None:
        """Unrealized P&L as percentage."""
        if self.unrealized_pnl is None or self.cost_basis == 0:
            return None
        return (self.unrealized_pnl / self.cost_basis) * 100

    def update_price(self, price: float, timestamp: str | None = None) -> None:
        """Update position with latest market price."""
        self.last_price = float(price)
        self.last_updated = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert position to dictionary."""
        return {
            "id": self.id,
            "ticker": self.ticker,
            "platform": self.platform,
            "name": self.name,
            "quantity": self.quantity,
            "avg_price": self.avg_price,
            "currency": self.currency,
            "type": self.type,
            "is_emergency_fund": self.is_emergency_fund,
            "purchase_date": self.purchase_date,
            "last_price": self.last_price,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        """Create position from dictionary."""
        pos = cls(
            ticker=data["ticker"],
            platform=data["platform"],
            quantity=data["quantity"],
            avg_price=data["avg_price"],
            currency=data.get("currency", "IDR"),
            position_type=data.get("type", "stock"),
            is_emergency_fund=data.get("is_emergency_fund", False),
            name=data.get("name"),
            purchase_date=data.get("purchase_date"),
            position_id=data.get("id"),
        )
        pos.last_price = data.get("last_price")
        pos.last_updated = data.get("last_updated")
        return pos


class PortfolioTracker:
    """Manages portfolio positions with persistence."""

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path) if data_path else PORTFOLIO_FILE
        self.positions: list[Position] = []
        self.metadata: dict[str, Any] = {
            "last_updated": None,
            "base_currency": "IDR",
            "usd_idr_rate": None,
        }
        self._load()

    def _load(self) -> None:
        """Load portfolio from disk."""
        if not self.data_path.exists():
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            self.positions = [Position.from_dict(p) for p in data.get("positions", [])]
            self.metadata = data.get("metadata", self.metadata)
        except (json.JSONDecodeError, KeyError):
            self.positions = []

    def save(self) -> None:
        """Persist portfolio to disk."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.metadata["total_positions"] = len(self.positions)

        data = {
            "positions": [p.to_dict() for p in self.positions],
            "metadata": self.metadata,
        }

        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_position(self, position: Position) -> Position:
        """Add new position to portfolio."""
        self.positions.append(position)
        self.save()
        return position

    def get_position(self, ticker: str, platform: str | None = None) -> Position | None:
        """Find position by ticker and optionally platform."""
        ticker = ticker.upper()
        for pos in self.positions:
            if pos.ticker == ticker:
                if platform is None or pos.platform == platform.lower():
                    return pos
        return None

    def get_position_by_id(self, position_id: str) -> Position | None:
        """Find position by ID."""
        for pos in self.positions:
            if pos.id == position_id:
                return pos
        return None

    def update_position(
        self,
        ticker: str,
        quantity: float | None = None,
        avg_price: float | None = None,
        platform: str | None = None,
    ) -> Position | None:
        """Update existing position."""
        pos = self.get_position(ticker, platform)
        if pos is None:
            return None

        if quantity is not None:
            pos.quantity = float(quantity)
        if avg_price is not None:
            pos.avg_price = float(avg_price)

        self.save()
        return pos

    def remove_position(self, ticker: str, platform: str | None = None) -> bool:
        """Remove position from portfolio."""
        pos = self.get_position(ticker, platform)
        if pos is None:
            return False

        self.positions.remove(pos)
        self.save()
        return True

    def get_all_positions(self) -> list[Position]:
        """Get all positions."""
        return self.positions.copy()

    def get_positions_by_platform(self, platform: str) -> list[Position]:
        """Get positions for specific platform."""
        platform = platform.lower()
        return [p for p in self.positions if p.platform == platform]

    def get_emergency_fund_positions(self) -> list[Position]:
        """Get all emergency fund positions."""
        return [p for p in self.positions if p.is_emergency_fund]

    def get_investment_positions(self) -> list[Position]:
        """Get all non-emergency fund positions."""
        return [p for p in self.positions if not p.is_emergency_fund]

    def total_cost_basis(self, currency: str | None = None) -> float:
        """Calculate total cost basis."""
        total = 0.0
        for pos in self.positions:
            if currency is None or pos.currency == currency.upper():
                total += pos.cost_basis
        return total

    def total_current_value(self, currency: str | None = None) -> float | None:
        """Calculate total current value (None if any price missing)."""
        total = 0.0
        for pos in self.positions:
            if currency is None or pos.currency == currency.upper():
                if pos.current_value is None:
                    return None
                total += pos.current_value
        return total

    def update_fx_rate(self, usd_idr_rate: float) -> None:
        """Update USD/IDR exchange rate in metadata."""
        self.metadata["usd_idr_rate"] = float(usd_idr_rate)
        self.save()

    def get_allocation_by_type(self) -> dict[str, float]:
        """Calculate allocation percentages by position type."""
        total = self.total_current_value()
        if total is None or total == 0:
            return {}

        allocations: dict[str, float] = {}
        for pos in self.positions:
            if pos.current_value is not None:
                ptype = pos.type
                allocations[ptype] = allocations.get(ptype, 0) + pos.current_value

        return {k: (v / total) * 100 for k, v in allocations.items()}

    def get_allocation_by_platform(self) -> dict[str, float]:
        """Calculate allocation percentages by platform."""
        total = self.total_current_value()
        if total is None or total == 0:
            return {}

        allocations: dict[str, float] = {}
        for pos in self.positions:
            if pos.current_value is not None:
                allocations[pos.platform] = allocations.get(pos.platform, 0) + pos.current_value

        return {k: (v / total) * 100 for k, v in allocations.items()}
