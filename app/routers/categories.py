from fastapi import APIRouter
from sqlmodel import select
from ..models import CreateCategory, Category
from ..database import GetSession
from ..crud.categories import GetCategory, CategoryByName


router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/")
async def create_category(session: GetSession, category: CreateCategory) -> Category:
 
    category = Category.model_validate(category, update={"name": category.name.title()})

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return category

@router.get("/{id}")
async def get_category(category: GetCategory) -> Category:
    return category

@router.get("/")
async def get_category_by_name(category: CategoryByName) -> Category:
    return category
