# TradingBOT

A lightweight trading system scaffold with both OANDA and MT5 broker adapters, market-data cleansing, regimes, drawdown risk logic, and a FastAPI/mobile interface.

## Included

- OANDA v20 adapter shell
- MT5 shell adapter
- Async tick-streaming foundation using `asyncio` + `websockets`
- Candle cleansing layer for missing data and spikes
- Simple regime classifier using K-means features
- Risk manager with kill-switch logic
- TimescaleDB schema stub
- FastAPI backend with JWT login and panic endpoint
- React Native mobile UI scaffold

## Quick start

```bash
python -m pip install -r requirements.txt
python -m uvicorn tradingbot.api.app:app --reload
```

Then open the mobile app under `mobile/` with Expo or React Native.

## Paper trading and TimescaleDB

Start the local database with Docker Compose:

```bash
docker compose up -d timescaledb
```

Compose initializes the `market_ticks` hypertable from `migrations/001_market_ticks.sql` on the first database start. The default local DSN is `postgresql://postgres:postgres@localhost:5432/tradingbot`.

The in-memory `PaperBroker` starts with a $10,000 balance and applies adverse 0.5-pip slippage to both entry and exit fills. Order volume is base-currency units. It is suitable for local strategy testing only; it does not model margin, financing, or broker-specific execution rules.

Run the websocket-to-database ingestion process after the database and a compatible tick websocket provider are available:

```bash
python -m tradingbot.ingestion.stream
```

The stream expects JSON object messages containing `timestamp` (or `time`), `symbol` (optional when the configured symbol is known), and `price` or `bid`/`ask`. Accepted ticks are normalized and stored in `market_ticks`; invalid prices and single-tick moves above the configured 15% guard are discarded. Docker's init scripts execute only for a new/empty volume; for an existing database, execute the migration manually or allow `TimescaleClient.ensure_schema()` to create the table.
