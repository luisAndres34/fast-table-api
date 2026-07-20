from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.encoders import jsonable_encoder
from app.api.dependencies import SessionDep, CurrentAdmin
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate, UserPublic
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

router = APIRouter(prefix="/users", tags=["users"])

def pagination_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    """
    Custom cache key generator.
    Ignores dynamic dependencies like 'session' and 'current_user'.
    """

    endpoint_kwargs = kwargs.get("kwargs") if "kwargs" in kwargs else kwargs
    
    skip = endpoint_kwargs.get("skip", 0)
    limit = endpoint_kwargs.get("limit", 100)
    
    return f"{namespace}:{func.__name__}:{skip}:{limit}"

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, session: SessionDep):
    """
    Create a new user.
    """
    user = await crud_user.get_by_email(session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    new_user = await crud_user.create(session=session, obj_in=user_in)
    await FastAPICache.clear(namespace="users") 
    return new_user

@router.get("/", response_model=list[UserPublic])
@cache(expire=60, namespace="users", key_builder=pagination_key_builder)
async def read_users(
    request: Request,
    response: Response,
    session: SessionDep, 
    admin: CurrentAdmin,
    skip: int = 0, 
    limit: int = 100
):
    """
    Retrieve users with pagination. (Requires Authentication)
    """
    users = await crud_user.get_multi(session=session, skip=skip, limit=limit)

    return jsonable_encoder(users)
