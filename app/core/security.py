from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def create_token(subject: str | Any, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
    return create_token(subject, expires_delta, "access")

def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
    return create_token(subject, expires_delta, "refresh")
