# create_superuser.py
import asyncio
from app.db.session import AsyncSessionLocal
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.logger import logger

async def create_user() -> None:
    logger.info("Forcing superuser creation...")
    async with AsyncSessionLocal() as session:
        user = await crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = UserCreate(
                name="Super Admin",
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role="admin"
            )
            await crud_user.create(session=session, obj_in=user_in)
            logger.info("✅ Superuser was created successfully!")
        else:
            logger.info("ℹ️ Superuser already exists, skipping creation.")

if __name__ == "__main__":
    asyncio.run(create_user())
