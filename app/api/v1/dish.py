from fastapi import APIRouter, HTTPException, status
import uuid

from app.api.dependencies import SessionDep, CurrentAdmin
from app.crud.dish import dish as crud_dish
from app.schemas.dish import DishCreate, DishPublic, DishUpdate


router = APIRouter(prefix="/dishes", tags=["dishes"])

@router.get("/", response_model=list[DishPublic])
async def get_dishes(session: SessionDep):
    """
    Public endpoint: Anyone can view the menu items.
    """
    return await crud_dish.get_multi(session=session)

@router.post("/", response_model=DishPublic, status_code=status.HTTP_201_CREATED)
async def create_dish(dish_in: DishCreate, session: SessionDep, admin: CurrentAdmin):
    """
    Protected endpoint: Only Admins can add new menu items.
    """
    return await crud_dish.create(session=session, obj_in=dish_in)

@router.patch("/{dish_id}", response_model=DishPublic)
async def update_existing_dish(
    dish_id: uuid.UUID, 
    dish_in: DishUpdate, 
    session: SessionDep, 
    admin: CurrentAdmin
):
    """
    Protected endpoint: Only Admins can update menu items.
    """
    db_dish = await crud_dish.get(session=session, id=dish_id)
    if not db_dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    return await crud_dish.update(session=session, db_obj=db_dish, obj_in=dish_in)

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_dish(
    dish_id: uuid.UUID, 
    session: SessionDep, 
    admin: CurrentAdmin
):
    """
    Protected endpoint: Only Admins can delete menu items.
    """
    db_dish = await crud_dish.get(session=session, id=dish_id)
    if not db_dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    await crud_dish.delete(session=session, id=dish_id)
    return None
