import asyncio

import pytest

from tradingbot.ingestion.cleansing import cleanse_tick
from tradingbot.ingestion import stream


def test_cleanse_tick_normalizes_timestamp_and_rejects_outlier():
    first = cleanse_tick(
        {"symbol": "EURUSD", "timestamp": "2026-01-01T00:00:00Z", "bid": 1.1, "ask": 1.1002}
    )
    assert first is not None
    assert first["price"] == pytest.approx(1.1001)
    assert cleanse_tick({"symbol": "EURUSD", "price": 1.5}, previous_price=1.1001) is None


def test_ingestion_cleans_and_persists_ticks():
    class FakeDatabase:
        def __init__(self):
            self.rows = []
            self.connected = False

        async def connect(self):
            self.connected = True

        async def ensure_schema(self):
            assert self.connected

        async def insert_tick(self, tick):
            self.rows.append(tick)

        async def close(self):
            self.connected = False

    async def ticks():
        yield {"symbol": "EURUSD", "timestamp": "2026-01-01T00:00:00Z", "bid": 1.1, "ask": 1.1002}
        yield {"symbol": "EURUSD", "timestamp": "2026-01-01T00:00:01Z", "price": 1.5}

    async def run_test():
        db = FakeDatabase()
        await stream.ingest_ticks("ws://not-used", "EURUSD", db, tick_source=ticks())
        assert len(db.rows) == 1
        assert db.rows[0]["symbol"] == "EURUSD"
        assert not db.connected

    asyncio.run(run_test())