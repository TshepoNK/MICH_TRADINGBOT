import os
from dataclasses import dataclass, field
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return configured_url

    user = quote_plus(os.getenv("DB_USER", "postgres"))
    password = quote_plus(os.getenv("DB_PASSWORD", "local-dev-only-change-me"))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = quote_plus(os.getenv("DB_NAME", "tradingbot"))
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


@dataclass(slots=True)
class Settings:
    """Application configuration with safe defaults for local/dev usage."""

    broker: str = "both"
    db_url: str = field(default_factory=_database_url)
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "tradingbot"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "local-dev-only-change-me"))
    timescale_enabled: bool = True
    max_daily_drawdown_pct: float = 2.0
    max_total_drawdown_pct: float = 5.0
    regime_confidence_threshold: float = 0.7
    use_live_broker: bool = False
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiry_minutes: int = 60
    api_username: str = field(default_factory=lambda: os.getenv("API_USERNAME", ""))
    api_password: str = field(default_factory=lambda: os.getenv("API_PASSWORD", ""))
    mt5_login: str | None = field(default_factory=lambda: os.getenv("MT5_LOGIN"))
    mt5_password: str | None = field(default_factory=lambda: os.getenv("MT5_PASSWORD"))
    mt5_server: str | None = field(default_factory=lambda: os.getenv("MT5_SERVER"))
    oanda_account_id: str | None = field(default_factory=lambda: os.getenv("OANDA_ACCOUNT_ID"))
    oanda_api_token: str | None = field(default_factory=lambda: os.getenv("OANDA_API_TOKEN"))
    oanda_environment: str = field(default_factory=lambda: os.getenv("OANDA_ENVIRONMENT", "practice"))
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    tick_socket_url: str = "ws://localhost:8765"
    supported_pairs: list[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])


settings = Settings()
