from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseBroker(ABC):
    """Abstract broker interface shared by paper and live broker adapters."""

    @abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def fetch_prices(self, symbol: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def place_order(self, symbol: str, side: str, volume: float, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def close_all_positions(self) -> dict[str, Any]:
        raise NotImplementedError


# Keep the original public name available for existing OANDA/MT5 integrations.
BrokerAdapter = BaseBroker
