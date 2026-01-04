"""Trade journal manager for tracking trades with thesis and notes."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

__all__ = [
    "JournalManager",
    "TradeEntry",
]


DATA_DIR = Path(__file__).parent.parent.parent / "data"
JOURNAL_FILE = DATA_DIR / "journal.json"


TradeAction = Literal["BUY", "SELL"]
TradeSentiment = Literal["confident", "neutral", "uncertain", "fearful", "greedy"]


class TradeEntry:

    def __init__(
        self,
        ticker: str,
        action: TradeAction,
        quantity: float,
        price: float,
        category: str = "id_stocks",
        currency: str = "IDR",
        thesis: str = "",
        notes: str = "",
        tags: list[str] | None = None,
        sentiment: TradeSentiment = "neutral",
        market_condition: str = "neutral",
        phase: int = 1,
        trade_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.id = trade_id or f"TRD-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
        self.timestamp = timestamp or datetime.now().isoformat()
        self.ticker = ticker.upper().strip()
        self.action = action.upper()
        self.quantity = float(quantity)
        self.price = float(price)
        self.category = category.lower().strip()
        self.currency = currency.upper().strip()
        self.thesis = thesis
        self.notes = notes
        self.tags = tags or []
        self.sentiment = sentiment
        self.market_condition = market_condition
        self.phase = phase
        self.fees: float = 0.0

    @property
    def total_value(self) -> float:
        """Total trade value excluding fees."""
        return self.quantity * self.price

    @property
    def total_with_fees(self) -> float:
        """Total trade value including fees."""
        if self.action == "BUY":
            return self.total_value + self.fees
        return self.total_value - self.fees

    def set_fees(self, fees: float) -> None:
        """Set trade fees."""
        self.fees = float(fees)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "category": self.category,
            "ticker": self.ticker,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "currency": self.currency,
            "total_value": self.total_value,
            "fees": self.fees,
            "thesis": self.thesis,
            "tags": self.tags,
            "notes": self.notes,
            "sentiment": self.sentiment,
            "market_condition": self.market_condition,
            "phase": self.phase,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradeEntry":
        category = data.get("category")
        if not category:
            old_platform = data.get("platform", "")
            currency = data.get("currency", "IDR")
            if old_platform == "bibit" or old_platform == "money_market":
                category = "emergency_fund"
            elif old_platform == "gotrade" or currency == "USD":
                category = "us_stocks"
            elif old_platform == "tokocrypto":
                category = "crypto"
            else:
                category = "id_stocks"

        entry = cls(
            ticker=data["ticker"],
            action=data["action"],
            quantity=data["quantity"],
            price=data["price"],
            category=category,
            currency=data.get("currency", "IDR"),
            thesis=data.get("thesis", ""),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            sentiment=data.get("sentiment", "neutral"),
            market_condition=data.get("market_condition", "neutral"),
            phase=data.get("phase", 1),
            trade_id=data.get("id"),
            timestamp=data.get("timestamp"),
        )
        entry.fees = data.get("fees", 0.0)
        return entry


class JournalManager:
    """Manages trade journal with persistence."""

    def __init__(self, data_path: str | Path | None = None):
        self.data_path = Path(data_path) if data_path else JOURNAL_FILE
        self.trades: list[TradeEntry] = []
        self.metadata: dict[str, Any] = {
            "last_updated": None,
            "total_trades": 0,
            "total_buys": 0,
            "total_sells": 0,
        }
        self._load()

    def _load(self) -> None:
        """Load journal from disk."""
        if not self.data_path.exists():
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            self.trades = [TradeEntry.from_dict(t) for t in data.get("trades", [])]
            self.metadata = data.get("metadata", self.metadata)
        except (json.JSONDecodeError, KeyError):
            self.trades = []

    def save(self) -> None:
        """Persist journal to disk."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self._update_metadata()

        data = {
            "trades": [t.to_dict() for t in self.trades],
            "metadata": self.metadata,
        }

        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _update_metadata(self) -> None:
        """Update journal metadata."""
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.metadata["total_trades"] = len(self.trades)
        self.metadata["total_buys"] = sum(1 for t in self.trades if t.action == "BUY")
        self.metadata["total_sells"] = sum(1 for t in self.trades if t.action == "SELL")

    def add_trade(self, trade: TradeEntry) -> TradeEntry:
        """Add new trade to journal."""
        self.trades.append(trade)
        self.save()
        return trade

    def get_trade(self, trade_id: str) -> TradeEntry | None:
        """Find trade by ID."""
        for trade in self.trades:
            if trade.id == trade_id:
                return trade
        return None

    def get_trades_by_ticker(self, ticker: str) -> list[TradeEntry]:
        """Get all trades for a ticker."""
        ticker = ticker.upper()
        return [t for t in self.trades if t.ticker == ticker]

    def get_recent_trades(self, limit: int = 10) -> list[TradeEntry]:
        """Get most recent trades."""
        sorted_trades = sorted(self.trades, key=lambda t: t.timestamp, reverse=True)
        return sorted_trades[:limit]

    def get_trades_in_range(
        self,
        start_date: datetime | str,
        end_date: datetime | str | None = None,
    ) -> list[TradeEntry]:
        """Get trades within date range."""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        if end_date is None:
            end_date = datetime.now()
        elif isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

        result = []
        for trade in self.trades:
            trade_dt = datetime.fromisoformat(trade.timestamp.replace("Z", "+00:00"))
            if start_date <= trade_dt <= end_date:
                result.append(trade)

        return sorted(result, key=lambda t: t.timestamp)

    def calculate_stats(self) -> dict[str, Any]:
        """Calculate trading statistics."""
        if not self.trades:
            return {
                "total_trades": 0,
                "buys": 0,
                "sells": 0,
                "total_bought": 0.0,
                "total_sold": 0.0,
                "net_flow": 0.0,
                "avg_trade_size": 0.0,
            }

        buys = [t for t in self.trades if t.action == "BUY"]
        sells = [t for t in self.trades if t.action == "SELL"]

        total_bought = sum(t.total_value for t in buys)
        total_sold = sum(t.total_value for t in sells)
        total_fees = sum(t.fees for t in self.trades)

        return {
            "total_trades": len(self.trades),
            "buys": len(buys),
            "sells": len(sells),
            "total_bought": total_bought,
            "total_sold": total_sold,
            "net_flow": total_sold - total_bought,
            "total_fees": total_fees,
            "avg_trade_size": sum(t.total_value for t in self.trades) / len(self.trades),
        }

    def get_trades_by_tag(self, tag: str) -> list[TradeEntry]:
        """Get all trades with specific tag."""
        tag = tag.lower()
        return [t for t in self.trades if tag in [tg.lower() for tg in t.tags]]

    def get_trades_by_sentiment(self, sentiment: TradeSentiment) -> list[TradeEntry]:
        """Get all trades with specific sentiment."""
        return [t for t in self.trades if t.sentiment == sentiment]

    def export_for_analysis(self) -> list[dict[str, Any]]:
        """Export trades as list of dicts for analysis."""
        return [t.to_dict() for t in self.trades]
