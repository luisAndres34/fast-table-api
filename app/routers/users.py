from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from ..models import Token, User, PublicUser, UserCreate
from ..database import GetSession
from ..auth import authenticate_user, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRES_MINUTES

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/token", response_model=Token)
def login_for_access_token(session: GetSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_token_time = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token({"sub": user.email}, expires_token_time)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/")
def create_user (session: GetSession, user: UserCreate) -> PublicUser:
    hashed_pwd = get_password_hash(user.password)
    user = User(**user.model_dump(exclude={"password"}), hashed_password=hashed_pwd)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

