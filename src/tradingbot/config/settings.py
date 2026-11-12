from dataclasses import dataclass, field


@dataclass(slots=True)
class Settings:
    """Application configuration with safe defaults for local/dev usage."""

    broker: str = "both"
    db_url: str = "postgresql://postgres:postgres@localhost:5432/tradingbot"
    timescale_enabled: bool = True
    max_daily_drawdown_pct: float = 2.0
    max_total_drawdown_pct: float = 5.0
    regime_confidence_threshold: float = 0.7
    use_live_broker: bool = False
    jwt_secret: str = "dev-secret-change-me"
    jwt_expiry_minutes: int = 60
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    tick_socket_url: str = "ws://localhost:8765"
    supported_pairs: list[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])


settings = Settings()
