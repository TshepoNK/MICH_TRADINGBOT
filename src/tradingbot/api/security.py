from __future__ import annotations

from datetime import datetime, timedelta

import jwt

from tradingbot.config.settings import settings


def create_token(username: str) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET_KEY must be configured before issuing tokens")
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET_KEY must be configured before verifying tokens")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return payload["sub"]
