from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import Annotated
from ..models import Item, FilterItem, UpdateItem, CreateItem, PublicItem
from ..database import GetSession
from ..utils import send_notification_email, write_audit_log, export_csv
from ..auth import get_current_user
from ..crud.categories import get_category_by_name

router = APIRouter(prefix="/items", tags=["items"], dependencies=[Depends(get_current_user)] )


async def get_item(id: int, session: GetSession) -> PublicItem:
    statement = select(Item).options(selectinload(Item.category)).where(Item.id == id)
    result = await session.execute(statement)
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item

GetItem = Annotated[Item, Depends(get_item)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: CreateItem, session: GetSession, background_tasks: BackgroundTasks) -> PublicItem:
    category = await get_category_by_name(session, item.category_name)
    item = Item.model_validate(item.model_dump() | {"category_id": category.id})
    session.add(item)
    await session.commit()
    await session.refresh(item, ["category"])
    background_tasks.add_task(send_notification_email, "admin@tienda.com", f"Se agregó el producto {item.name}")

    return item

@router.post("/export")
async def export(background_tasks: BackgroundTasks):
    background_tasks.add_task(export_csv)
    return{"message": "La exportación ha comenzado. Te avisaremos cuando termine."}

@router.get("/{id}")
async def get_item_by_id(item: GetItem) -> PublicItem:
    return item

@router.get("/")
async def get_items(session: GetSession, item_filter: Annotated[FilterItem, Depends()]) -> list[PublicItem]:
    statement = select(Item).options(selectinload(Item.category))

    if item_filter.name is not None:
        statement = statement.where(Item.name.contains(item_filter.name))

    if item_filter.exact_price is not None:
        statement = statement.where(Item.price == item_filter.exact_price)
    
    if item_filter.min_price is not None:
        statement = statement.where(Item.price >= item_filter.min_price)

    if item_filter.max_price is not None:
        statement = statement.where(Item.price <= item_filter.max_price)

    if item_filter.stock is not None:
        statement = statement.where(Item.stock == item_filter.stock)

    result = await session.execute(statement)
    items = result.scalars().all()

    return items

@router.patch("/{id}")
async def update_item(session: GetSession, item: GetItem, item_data: UpdateItem, background_tasks: BackgroundTasks) -> PublicItem:


    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    session.add(item)
    await session.commit()
    await session.refresh(item, ["category"])

    if item_data.price is not None:
        background_tasks.add_task(write_audit_log, item.id, item_data.price)

    return item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(session: GetSession, item: GetItem):
    await session.delete(item)
    await session.commit()

    return None
