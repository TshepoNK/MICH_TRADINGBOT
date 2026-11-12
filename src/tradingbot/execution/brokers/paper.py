from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Any

from tradingbot.execution.base import BaseBroker


@dataclass(slots=True)
class PaperPosition:
    id: str
    symbol: str
    side: str
    volume: float
    entry_price: float


class PaperBroker(BaseBroker):
    """In-memory broker simulator. Volume is expressed in base-currency units."""

    def __init__(self, initial_balance: float = 10_000.0, slippage_pips: float = 0.5):
        if initial_balance <= 0:
            raise ValueError("initial_balance must be positive")
        if slippage_pips < 0:
            raise ValueError("slippage_pips cannot be negative")
        self.balance = float(initial_balance)
        self.initial_balance = float(initial_balance)
        self.slippage_pips = float(slippage_pips)
        self.connected = False
        self.market_prices: dict[str, dict[str, float]] = {}
        self.positions: dict[str, PaperPosition] = {}
        self._position_ids = count(1)

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    @staticmethod
    def _pip_size(symbol: str) -> float:
        return 0.01 if symbol.upper().endswith("JPY") else 0.0001

    def set_market_price(self, symbol: str, bid: float, ask: float) -> None:
        if bid <= 0 or ask < bid:
            raise ValueError("prices must be positive and ask must be at least bid")
        self.market_prices[symbol.upper()] = {"bid": float(bid), "ask": float(ask)}

    def fetch_prices(self, symbol: str) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        quote = self.market_prices.get(symbol.upper())
        if quote is None:
            raise LookupError(f"no paper market price available for {symbol}")
        return {"symbol": symbol.upper(), **quote}

    def place_order(self, symbol: str, side: str, volume: float, **kwargs: Any) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        normalized_side = side.lower()
        if normalized_side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")
        if volume <= 0:
            raise ValueError("volume must be positive")

        quote = self.fetch_prices(symbol)
        slippage = self.slippage_pips * self._pip_size(symbol)
        fill_price = quote["ask"] + slippage if normalized_side == "buy" else quote["bid"] - slippage
        position_id = str(next(self._position_ids))
        position = PaperPosition(position_id, symbol.upper(), normalized_side, float(volume), fill_price)
        self.positions[position_id] = position
        return {
            "id": position_id,
            "symbol": position.symbol,
            "side": position.side,
            "volume": position.volume,
            "fill_price": fill_price,
            "status": "filled",
        }

    def close_position(self, position_id: str) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        try:
            position = self.positions[position_id]
        except KeyError as exc:
            raise LookupError(f"unknown paper position: {position_id}") from exc

        quote = self.fetch_prices(position.symbol)
        slippage = self.slippage_pips * self._pip_size(position.symbol)
        is_long = position.side == "buy"
        exit_price = quote["bid"] - slippage if is_long else quote["ask"] + slippage
        pnl = (exit_price - position.entry_price) * position.volume
        if not is_long:
            pnl = -pnl
        self.balance += pnl
        del self.positions[position_id]
        return {
            "id": position_id,
            "symbol": position.symbol,
            "exit_price": exit_price,
            "realized_pnl": pnl,
            "balance": self.balance,
            "status": "closed",
        }

    def close_all_positions(self) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("paper broker is not connected")
        closed = [self.close_position(position_id) for position_id in list(self.positions)]
        return {"status": "closed", "count": len(closed), "positions": closed}

    @property
    def unrealized_pnl(self) -> float:
        total = 0.0
        for position in self.positions.values():
            quote = self.market_prices.get(position.symbol)
            if quote is None:
                continue
            mark = quote["bid"] if position.side == "buy" else quote["ask"]
            direction = 1.0 if position.side == "buy" else -1.0
            total += (mark - position.entry_price) * position.volume * direction
        return total

    @property
    def equity(self) -> float:
        return self.balance + self.unrealized_pnl