from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from tradingbot.api.security import create_token, verify_token

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
    if payload.username == "admin" and payload.password == "admin123":
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
