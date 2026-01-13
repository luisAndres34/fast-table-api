from ..models import Category
from ..database import GetSession
from fastapi import Depends, status, HTTPException
from typing import Annotated
from sqlmodel import select 

async def get_category_by_id(session: GetSession, id: int) -> Category:
    category = await session.get(Category, id)

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category

GetCategory = Annotated[Category, Depends(get_category_by_id)]

async def get_category_by_name(session: GetSession, category_name: str) -> Category:
    statement = select(Category).where(Category.name == category_name.title())
    
    result = await session.execute(statement)
    category = result.scalars().first()

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category

CategoryByName  = Annotated[Category, Depends(get_category_by_name)]
