from datetime import timedelta
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import user as crud_user
from app.core.logger import logger
from app.schemas.token import Token, RefreshTokenReq

router = APIRouter(tags=["authentication"])

@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
) -> Token:
    user = await crud_user.authenticate(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)

    return Token(
        access_token=access_token, 
        refresh_token=refresh_token, 
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: RefreshTokenReq,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """
    Use the refresh_token to acquire a new pair of access and refresh tokens.
    """
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
            
        email: str | None = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired refresh token"
        )

    user = await crud_user.get_by_email(session, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found or inactive"
        )

    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)
    
    return Token(
        access_token=new_access_token, 
        refresh_token=new_refresh_token, 
        token_type="bearer"
    )
