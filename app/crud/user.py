from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        statement = select(self.model).where(self.model.email == email)
        result = await session.execute(statement)
        return result.scalars().first()

    async def authenticate(self, session: AsyncSession, email: str, password: str) -> User | None:
        user = await self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create(self, session: AsyncSession, obj_in: UserCreate) -> User:
        hashed_pwd = get_password_hash(obj_in.password)
        user_data = obj_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_pwd
        db_obj = self.model(**user_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

user = CRUDUser(User)
