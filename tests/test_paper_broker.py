import pytest

from tradingbot.execution.brokers.paper import PaperBroker


def test_paper_broker_applies_adverse_half_pip_slippage_and_tracks_pnl():
    broker = PaperBroker(initial_balance=10_000, slippage_pips=0.5)
    assert broker.connect()
    broker.set_market_price("EURUSD", bid=1.1000, ask=1.1002)

    opened = broker.place_order("EURUSD", "buy", 10_000)
    assert opened["fill_price"] == pytest.approx(1.10025)
    assert broker.balance == pytest.approx(10_000)

    broker.set_market_price("EURUSD", bid=1.1010, ask=1.1012)
    closed = broker.close_position(opened["id"])

    assert closed["exit_price"] == pytest.approx(1.10095)
    assert closed["realized_pnl"] == pytest.approx(7.0)
    assert broker.balance == pytest.approx(10_007.0)
    assert broker.positions == {}


def test_paper_broker_close_all_liquidates_in_memory_positions():
    broker = PaperBroker()
    broker.connect()
    broker.set_market_price("USDJPY", bid=150.0, ask=150.02)
    broker.place_order("USDJPY", "sell", 1_000)

    result = broker.close_all_positions()

    assert result["count"] == 1
    assert broker.positions == {}


def test_paper_broker_rejects_invalid_order():
    broker = PaperBroker()
    broker.connect()
    with pytest.raises(ValueError):
        broker.place_order("EURUSD", "hold", 1)