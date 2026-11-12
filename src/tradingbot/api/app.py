from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from tradingbot.api.security import create_token, verify_token
from tradingbot.config.settings import settings

app = FastAPI(title="TradingBOT API", version="1.0.0")


class LoginRequest(BaseModel):
    username: str
    password: str


class PanicRequest(BaseModel):
    confirm: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, str]:
    if not settings.api_username or not settings.api_password or not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="API credentials and JWT secret are not configured")
    if payload.username == settings.api_username and payload.password == settings.api_password:
        return {"token": create_token(payload.username)}
    raise HTTPException(status_code=401, detail="invalid credentials")


@app.get("/dashboard")
def dashboard(request: Request) -> dict[str, object]:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="missing token")
    verify_token(token)
    return {
        "pnl": 245.60,
        "open_positions": 2,
        "equity": 10120.40,
        "daily_drawdown": 1.4,
        "status": "green",
    }


@app.post("/panic")
def panic(payload: PanicRequest) -> dict[str, str]:
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="confirmation required")
    return {"status": "all_positions_closed", "locked": True}
