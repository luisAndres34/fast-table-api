from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Annotated
from .database import GetSession
from .models import User
from .config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = settings.ACCESS_TOKEN_EXPIRES_MINUTES
SECRET_KEY = settings.SECRET_KEY

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(plain_password):
    return password_hash.hash(plain_password)

async def get_user(session: AsyncSession, email) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def authenticate_user(session: AsyncSession, email, password):
    user = await get_user(session, email)

    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta

    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)

    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

async def get_current_user(session: GetSession, token: Annotated[str, Depends(oauth_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't verify credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = await get_user(session, email)

    if not user:
        raise credentials_exception
    
    return user
