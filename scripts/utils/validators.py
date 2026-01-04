"""Input validation utilities."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

__all__ = [
    "validate_ticker",
    "validate_currency",
    "validate_quantity",
    "validate_price",
    "validate_date",
    "validate_platform",
    "validate_position_type",
    "validate_percentage",
    "ValidationError",
]


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


VALID_PLATFORMS = frozenset({"bibit", "stockbit", "gotrade", "tokocrypto", "other"})
VALID_CURRENCIES = frozenset({"IDR", "USD"})
VALID_POSITION_TYPES = frozenset({"stock", "crypto", "money_market", "etf", "bond", "other"})

TICKER_PATTERN = re.compile(r"^[A-Z0-9][\w\-.]{0,19}$", re.IGNORECASE)


def validate_ticker(ticker: Any) -> str:
    """Validate and normalize ticker symbol."""
    if not ticker or not isinstance(ticker, str):
        raise ValidationError("Ticker must be a non-empty string")

    ticker = ticker.strip().upper()

    if not TICKER_PATTERN.match(ticker):
        raise ValidationError(
            f"Invalid ticker format: {ticker}. Must be 1-20 alphanumeric characters."
        )

    return ticker


def validate_currency(currency: Any) -> str:
    """Validate and normalize currency code."""
    if not currency or not isinstance(currency, str):
        raise ValidationError("Currency must be a non-empty string")

    currency = currency.strip().upper()

    if currency not in VALID_CURRENCIES:
        raise ValidationError(
            f"Invalid currency: {currency}. Valid options: {', '.join(sorted(VALID_CURRENCIES))}"
        )

    return currency


def validate_quantity(quantity: Any, allow_zero: bool = False) -> float:
    """Validate quantity value."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Quantity must be a number, got: {quantity}") from e

    if qty < 0:
        raise ValidationError(f"Quantity cannot be negative: {qty}")

    if not allow_zero and qty == 0:
        raise ValidationError("Quantity cannot be zero")

    return qty


def validate_price(price: Any, allow_zero: bool = False) -> float:
    """Validate price value."""
    try:
        p = float(price)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Price must be a number, got: {price}") from e

    if p < 0:
        raise ValidationError(f"Price cannot be negative: {p}")

    if not allow_zero and p == 0:
        raise ValidationError("Price cannot be zero")

    return p


def validate_date(date_input: Any) -> datetime:
    """Validate and parse date input."""
    if isinstance(date_input, datetime):
        return date_input

    if not isinstance(date_input, str):
        raise ValidationError(f"Date must be a string or datetime, got: {type(date_input)}")

    date_str = date_input.strip()

    formats_to_try = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]

    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str.replace("Z", "+0000"), fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        pass

    raise ValidationError(f"Could not parse date: {date_str}. Use YYYY-MM-DD format.")


def validate_platform(platform: Any) -> str:
    """Validate and normalize platform name."""
    if not platform or not isinstance(platform, str):
        raise ValidationError("Platform must be a non-empty string")

    platform = platform.strip().lower()

    if platform not in VALID_PLATFORMS:
        raise ValidationError(
            f"Invalid platform: {platform}. Valid options: {', '.join(sorted(VALID_PLATFORMS))}"
        )

    return platform


def validate_position_type(position_type: Any) -> str:
    """Validate and normalize position type."""
    if not position_type or not isinstance(position_type, str):
        raise ValidationError("Position type must be a non-empty string")

    pos_type = position_type.strip().lower()

    if pos_type not in VALID_POSITION_TYPES:
        raise ValidationError(
            f"Invalid position type: {pos_type}. Valid options: {', '.join(sorted(VALID_POSITION_TYPES))}"
        )

    return pos_type


def validate_percentage(value: Any, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Validate percentage value."""
    try:
        pct = float(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Percentage must be a number, got: {value}") from e

    if pct < min_val or pct > max_val:
        raise ValidationError(f"Percentage must be between {min_val} and {max_val}, got: {pct}")

    return pct
