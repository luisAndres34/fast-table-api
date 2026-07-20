from fastapi import APIRouter, HTTPException, status
import uuid

from app.api.dependencies import SessionDep, CurrentAdmin
from app.crud.category import category as crud_category
from app.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate



router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryPublic])
async def get_categories(session: SessionDep):
    return await crud_category.get_multi(session=session)

@router.post("/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, session: SessionDep, admin: CurrentAdmin):
    return await crud_category.create(session=session, obj_in=category_in)

@router.patch("/{category_id}", response_model=CategoryPublic)
async def update_existing_category(
    category_id: uuid.UUID, 
    category_in: CategoryUpdate, 
    session: SessionDep, 
    admin: CurrentAdmin
):
    db_category = await crud_category.get(session=session, id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return await crud_category.update(session=session, db_obj=db_category, obj_in=category_in)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: uuid.UUID, 
    session: SessionDep, 
    admin: CurrentAdmin
):
    db_category = await crud_category.get(session=session, id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await crud_category.delete(session=session, id=category_id)
    return None
