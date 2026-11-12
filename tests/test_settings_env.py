import pytest
from fastapi import HTTPException

from tradingbot.api.app import LoginRequest, login
from tradingbot.api.security import create_token
from tradingbot.config.settings import _database_url, settings
from tradingbot.execution.brokers.mt5 import MetaTrader5Adapter
from tradingbot.execution.brokers.oanda import OandaBrokerAdapter


def test_database_url_reads_db_environment_and_encodes_password(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "trader")
    monkeypatch.setenv("DB_PASSWORD", "p@ss/word")
    monkeypatch.setenv("DB_HOST", "db.local")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "ticks")

    assert _database_url() == "postgresql://trader:p%40ss%2Fword@db.local:5433/ticks"


def test_login_is_disabled_without_credentials_or_jwt_secret(monkeypatch):
    monkeypatch.setattr(settings, "api_username", "")
    monkeypatch.setattr(settings, "api_password", "")
    monkeypatch.setattr(settings, "jwt_secret", "")

    with pytest.raises(HTTPException) as error:
        login(LoginRequest(username="admin", password="admin123"))

    assert error.value.status_code == 503


def test_jwt_creation_requires_configured_secret(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_token("trader")


def test_broker_adapters_use_environment_backed_settings(monkeypatch):
    monkeypatch.setattr(settings, "mt5_login", "12345678")
    monkeypatch.setattr(settings, "mt5_password", "demo-password")
    monkeypatch.setattr(settings, "mt5_server", "Demo-Server")
    monkeypatch.setattr(settings, "oanda_account_id", "practice-account")
    monkeypatch.setattr(settings, "oanda_api_token", "practice-token")
    monkeypatch.setattr(settings, "oanda_environment", "practice")

    mt5 = MetaTrader5Adapter()
    oanda = OandaBrokerAdapter()

    assert (mt5.login, mt5.password, mt5.server) == (
        "12345678",
        "demo-password",
        "Demo-Server",
    )
    assert (oanda.account_id, oanda.token, oanda.env) == (
        "practice-account",
        "practice-token",
        "practice",
    )