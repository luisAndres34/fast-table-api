from fastapi import APIRouter, HTTPException, status
from app.api.dependencies import SessionDep, CurrentAdmin
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


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

    return await crud_user.create(session=session, obj_in=user_in)


@router.get("/", response_model=list[UserPublic])
async def read_users(
    session: SessionDep, 
    admin: CurrentAdmin,
    skip: int = 0, 
    limit: int = 100
):
    """
    Retrieve users with pagination. (Requires Authentication)
    """
    return await crud_user.get_multi(session=session, skip=skip, limit=limit)
