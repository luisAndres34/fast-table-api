from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import UserRole

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.crud.user import user as crud_user

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token"
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected access token.",
            )
            
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except InvalidTokenError:
        raise credentials_exception

    user = await crud_user.get_by_email(session, email=email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

def verify_role(allowed_roles: list[UserRole]):
    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="The user doesn't have enough privileges"
            )
        return current_user
    return role_checker

CurrentAdmin = Annotated[User, Depends(verify_role([UserRole.admin]))]
CurrentStaff = Annotated[User, Depends(verify_role([UserRole.admin, UserRole.waiter]))]
