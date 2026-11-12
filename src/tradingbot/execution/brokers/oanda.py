from __future__ import annotations

from typing import Any

from tradingbot.config.settings import settings
from tradingbot.execution.base import BrokerAdapter


class OandaBrokerAdapter(BrokerAdapter):
    """Minimal OANDA v20-compatible adapter shell."""

    def __init__(self, account_id: str | None = None, token: str | None = None, env: str = "practice"):
        self.account_id = account_id or settings.oanda_account_id
        self.token = token or settings.oanda_api_token
        self.env = env or settings.oanda_environment
        self.connected = False

    def connect(self) -> bool:
        self.connected = bool(self.account_id and self.token)
        return self.connected

    def disconnect(self) -> None:
        self.connected = False

    def fetch_prices(self, symbol: str) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("OANDA adapter is not connected")
        return {"symbol": symbol, "bid": 1.0, "ask": 1.0005, "time": "now"}

    def place_order(self, symbol: str, side: str, volume: float, **kwargs: Any) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("OANDA adapter is not connected")
        return {"symbol": symbol, "side": side, "volume": volume, "status": "filled"}

    def close_all_positions(self) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("OANDA adapter is not connected")
        return {"status": "closed", "count": 0}
