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

```powershell
py -m pip install -e ".[dev]"
Copy-Item .env.example .env
py -m uvicorn tradingbot.api.app:app --reload
```

Before starting the API, replace every placeholder in `.env`, including `API_USERNAME`, `API_PASSWORD`, and `JWT_SECRET_KEY`. Generate a JWT key locally with `python -c "import secrets; print(secrets.token_hex(32))"`. Do not commit or share `.env`; `.gitignore` excludes it. The MT5 and OANDA values are optional for paper trading.

Then open the mobile app under `mobile/` with Expo or React Native.

## Paper trading and TimescaleDB

Start the local database with Docker Compose:

```bash
docker compose up -d timescaledb
```

Compose initializes the `market_ticks` hypertable from `migrations/001_market_ticks.sql` on the first database start. It uses `DB_NAME`, `DB_USER`, and `DB_PASSWORD` from `.env`; the application constructs its PostgreSQL DSN from the same settings. If the database volume was already initialized, changing `.env` does not change the existing database user's password.

The in-memory `PaperBroker` starts with a $10,000 balance and applies adverse 0.5-pip slippage to both entry and exit fills. Order volume is base-currency units. It is suitable for local strategy testing only; it does not model margin, financing, or broker-specific execution rules.

Run the websocket-to-database ingestion process after the database and a compatible tick websocket provider are available:

```bash
python -m tradingbot.ingestion.stream
```

The stream expects JSON object messages containing `timestamp` (or `time`), `symbol` (optional when the configured symbol is known), and `price` or `bid`/`ask`. Accepted ticks are normalized and stored in `market_ticks`; invalid prices and single-tick moves above the configured 15% guard are discarded. Docker's init scripts execute only for a new/empty volume; for an existing database, execute the migration manually or allow `TimescaleClient.ensure_schema()` to create the table.
