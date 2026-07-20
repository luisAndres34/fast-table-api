from typing import Generic, TypeVar, Any
from sqlmodel import select, SQLModel
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> ModelType | None:
        return await session.get(self.model, id)

    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.execute(statement)
        return result.scalars().all()

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:

        update_data = obj_in.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: Any) -> ModelType | None:
        db_obj = await session.get(self.model, id)
        if db_obj:
            await session.delete(db_obj)
            await session.commit()
        return db_obj

    async def get_by_attribute(self, session: AsyncSession, column_name: str, value: Any) -> ModelType | None:
        column = getattr(self.model, column_name)
        statement = select(self.model).where(column == value)
        result = await session.execute(statement)
        return result.scalars().first()
