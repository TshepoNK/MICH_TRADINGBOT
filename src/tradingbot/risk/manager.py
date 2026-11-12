from __future__ import annotations


class RiskManager:
    """Simple risk controller with drawdown kill-switch logic."""

    def __init__(self, max_daily_drawdown_pct: float = 2.0, max_total_drawdown_pct: float = 5.0):
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.max_total_drawdown_pct = max_total_drawdown_pct
        self.current_drawdown = 0.0
        self.locked = False

    def should_liquidate(self) -> bool:
        if self.locked:
            return True
        return self.current_drawdown >= self.max_daily_drawdown_pct or self.current_drawdown >= self.max_total_drawdown_pct

    def liquidate(self) -> None:
        self.locked = True


def position_size_from_atr(balance: float, atr: float, risk_pct: float = 0.01, stop_distance: float = 0.008) -> float:
    """Return a volatility-adjusted position size capped to the available balance."""
    risk_amount = max(balance * risk_pct, 0.0)
    distance = max(stop_distance, 1e-9)
    return min(risk_amount / distance, balance)
