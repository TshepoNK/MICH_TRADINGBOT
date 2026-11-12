from __future__ import annotations

import json
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable
from typing import Any

import websockets

from tradingbot.ingestion.cleansing import cleanse_tick


async def stream_ticks(url: str, symbol: str) -> AsyncIterator[dict[str, Any]]:
    """Subscribe to a websocket and yield decoded object-shaped tick messages."""
    async with websockets.connect(url) as websocket:
        await websocket.send(f"subscribe:{symbol}")
        while True:
            message = await websocket.recv()
            try:
                payload = json.loads(message)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(payload, dict):
                yield payload


async def consume_ticks(
    url: str,
    symbol: str,
    callback: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    async for tick in stream_ticks(url, symbol):
        await callback(tick)


async def ingest_ticks(
    url: str,
    symbol: str,
    database: Any,
    *,
    tick_source: AsyncIterable[dict[str, Any]] | None = None,
) -> None:
    """Clean websocket ticks and persist them until the stream ends or fails."""
    await database.connect()
    try:
        await database.ensure_schema()
        source = tick_source if tick_source is not None else stream_ticks(url, symbol)
        previous_prices: dict[str, float] = {}
        async for message in source:
            if not isinstance(message, dict):
                continue
            tick = cleanse_tick(
                {**message, "symbol": message.get("symbol", symbol)},
                previous_price=previous_prices.get(symbol.upper()),
            )
            if tick is None:
                continue
            await database.insert_tick(tick)
            previous_prices[tick["symbol"]] = tick["price"]
    finally:
        await database.close()


async def main() -> None:
    from tradingbot.config.settings import settings
    from tradingbot.storage.timescaledb import TimescaleClient

    database = TimescaleClient(settings.db_url)
    await ingest_ticks(settings.tick_socket_url, "EURUSD", database)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())