from __future__ import annotations

from collections.abc import Sequence
from typing import Any


SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS market_ticks (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL CHECK (price > 0),
    bid DOUBLE PRECISION,
    ask DOUBLE PRECISION,
    volume DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (volume >= 0)
);

SELECT create_hypertable('market_ticks', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS market_ticks_symbol_time_idx
    ON market_ticks (symbol, time DESC);
"""


class TimescaleClient:
    """Async TimescaleDB client used by the websocket tick ingestion pipeline."""

    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 5):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool: Any = None

    async def connect(self) -> None:
        if self._pool is None:
            import asyncpg

            self._pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=self.min_size,
                max_size=self.max_size,
            )

    async def ensure_schema(self) -> None:
        await self.connect()
        async with self._pool.acquire() as connection:
            await connection.execute(SCHEMA_SQL)

    async def insert_tick(self, tick: dict[str, Any]) -> None:
        await self.connect()
        async with self._pool.acquire() as connection:
            await connection.execute(
                """INSERT INTO market_ticks (time, symbol, price, bid, ask, volume)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                tick["time"],
                tick["symbol"],
                tick["price"],
                tick.get("bid"),
                tick.get("ask"),
                tick.get("volume", 0.0),
            )

    async def insert_ticks(self, ticks: Sequence[dict[str, Any]]) -> int:
        if not ticks:
            return 0
        await self.connect()
        records = [
            (
                tick["time"],
                tick["symbol"],
                tick["price"],
                tick.get("bid"),
                tick.get("ask"),
                tick.get("volume", 0.0),
            )
            for tick in ticks
        ]
        async with self._pool.acquire() as connection:
            await connection.executemany(
                """INSERT INTO market_ticks (time, symbol, price, bid, ask, volume)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                records,
            )
        return len(records)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None