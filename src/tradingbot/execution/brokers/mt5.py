from __future__ import annotations

from typing import Any

from tradingbot.execution.base import BrokerAdapter


class MetaTrader5Adapter(BrokerAdapter):
    """Minimal MT5 adapter shell for local desktop integration."""

    def __init__(self, login: str | None = None, password: str | None = None, server: str | None = None):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False

    def connect(self) -> bool:
        self.connected = bool(self.login and self.password and self.server)
        return self.connected

    def disconnect(self) -> None:
        self.connected = False

    def fetch_prices(self, symbol: str) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("MT5 adapter is not connected")
        return {"symbol": symbol, "bid": 1.0, "ask": 1.0004, "time": "now"}

    def place_order(self, symbol: str, side: str, volume: float, **kwargs: Any) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("MT5 adapter is not connected")
        return {"symbol": symbol, "side": side, "volume": volume, "status": "filled"}

    def close_all_positions(self) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("MT5 adapter is not connected")
        return {"status": "closed", "count": 0}
