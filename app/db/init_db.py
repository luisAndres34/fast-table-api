from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.logger import logger

async def init_db(session: AsyncSession) -> None:
    """
    Initialize the database with default data.
    Creates the first superuser if it doesn't exist.
    """
    logger.info("Starting database initialization...")
    
    user = await crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
    
    if not user:
        user_in = UserCreate(
            name="Super Admin",
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role="admin"
        )
        await crud_user.create(session=session, obj_in=user_in)
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} was successfully created.")
    else:
        logger.info("Superuser already exists. Skipping creation.")
