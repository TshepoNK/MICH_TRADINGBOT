import pandas as pd
import pytest

from tradingbot.ingestion.cleansing import cleanse_candles
from tradingbot.ml.regime import RegimeFilter
from tradingbot.risk.manager import RiskManager, position_size_from_atr
from tradingbot.utils.retry import retry


def test_cleanse_candles_handles_missing_and_spikes():
    candles = pd.DataFrame(
        {
            "open": [1.1000, 1.1010, None, 1.1050, 1.1060],
            "high": [1.1020, 1.1030, 1.1040, 1.1800, 1.1070],
            "low": [1.0990, 1.1000, 1.1010, 1.1030, 1.1050],
            "close": [1.1010, 1.1020, 1.1030, 1.1040, 1.1060],
            "volume": [100, 110, 120, 130, 140],
        }
    )

    cleaned = cleanse_candles(candles, max_spike_ratio=0.15)

    assert cleaned["high"].isna().sum() == 0
    assert cleaned["open"].notna().all()
    assert cleaned.loc[3, "high"] < 1.15


def test_regime_filter_classifies_daily_states():
    closes = pd.Series([1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.04, 1.03, 1.02, 1.01])
    filter_model = RegimeFilter(n_clusters=3)
    labels = filter_model.classify(closes)

    assert set(labels).issubset({"Trending", "Ranging", "Volatile"})
    assert len(labels) == len(closes)


def test_position_size_is_volatility_adjusted():
    size = position_size_from_atr(balance=10000, atr=0.008, risk_pct=0.01, stop_distance=0.008)
    assert size > 0
    assert size <= 10000


def test_risk_manager_kill_switch_threshold():
    manager = RiskManager(max_daily_drawdown_pct=2.0, max_total_drawdown_pct=5.0)
    manager.current_drawdown = 2.1
    assert manager.should_liquidate() is True


def test_retry_decorator_retries_transient_failure():
    calls = {"count": 0}

    @retry(retries=2, base_delay=0.0)
    def flaky():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("transient")
        return "ok"

    assert flaky() == "ok"
    assert calls["count"] == 2
