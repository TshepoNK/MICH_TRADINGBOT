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