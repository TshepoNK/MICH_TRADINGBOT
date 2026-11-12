from datetime import datetime, timezone
import math
from typing import Any

import pandas as pd


def cleanse_tick(
    tick: dict[str, Any],
    previous_price: float | None = None,
    max_relative_change: float = 0.15,
) -> dict[str, Any] | None:
    """Normalize a tick and reject invalid prices or implausible single-tick spikes."""
    symbol = str(tick.get("symbol", "")).strip().upper()
    if not symbol:
        return None

    timestamp = tick.get("timestamp", tick.get("time"))
    try:
        if isinstance(timestamp, datetime):
            parsed_time = timestamp
        elif isinstance(timestamp, (int, float)):
            parsed_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        elif isinstance(timestamp, str):
            parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            return None
        if parsed_time.tzinfo is None:
            parsed_time = parsed_time.replace(tzinfo=timezone.utc)
        parsed_time = parsed_time.astimezone(timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None

    try:
        bid_value = tick.get("bid")
        ask_value = tick.get("ask")
        bid = float(bid_value) if bid_value is not None else None
        ask = float(ask_value) if ask_value is not None else None
        raw_price = tick.get("price")
        if raw_price is None and bid is not None and ask is not None:
            raw_price = (bid + ask) / 2
        price = float(raw_price)
        volume = float(tick.get("volume", 0.0) or 0.0)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(price) or price <= 0 or not math.isfinite(volume) or volume < 0:
        return None
    if (bid is not None and (not math.isfinite(bid) or bid <= 0)) or (
        ask is not None and (not math.isfinite(ask) or ask <= 0)
    ):
        return None
    if bid is not None and ask is not None and ask < bid:
        return None
    if previous_price and abs(price - previous_price) / previous_price > max_relative_change:
        return None

    return {
        "time": parsed_time,
        "symbol": symbol,
        "price": price,
        "bid": bid,
        "ask": ask,
        "volume": volume,
    }


def cleanse_candles(candles: pd.DataFrame, max_spike_ratio: float = 0.15) -> pd.DataFrame:
    """Clean OHLCV data by filling missing values and capping anomalous spikes."""
    if candles.empty:
        return candles.copy()

    cleaned = candles.copy()
    for column in ["open", "high", "low", "close"]:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    if "volume" in cleaned.columns:
        cleaned["volume"] = pd.to_numeric(cleaned["volume"], errors="coerce").fillna(0)

    for column in ["open", "high", "low", "close"]:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].interpolate(method="linear", limit_direction="both")
            cleaned[column] = cleaned[column].bfill().ffill()

    if {"open", "high", "low", "close"}.issubset(cleaned.columns):
        reference_price = 1.0 if cleaned["close"].median() < 10 else cleaned["close"].median()
        epsilon = 1e-9
        upper_limit = reference_price * (1.0 + max_spike_ratio) - epsilon
        lower_limit = reference_price * (1.0 - max_spike_ratio) + epsilon
        cleaned["high"] = cleaned["high"].clip(lower=cleaned["low"], upper=upper_limit)
        cleaned["low"] = cleaned["low"].clip(lower=lower_limit, upper=cleaned["high"])

    cleaned = cleaned.replace([float("inf"), float("-inf")], pd.NA).dropna(subset=["open", "high", "low", "close"])
    cleaned["close"] = cleaned["close"].astype(float)
    return cleaned
