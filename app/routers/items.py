from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlmodel import select
from typing import Annotated
from ..models import Item, ItemBase, FilterItem, UpdateItem
from ..database import GetSession
from ..utils import send_notification_email, write_audit_log, export_csv
from ..auth import get_current_user

router = APIRouter(prefix="/items", tags=["items"], dependencies=[Depends(get_current_user)] )


def get_item(id: int, session: GetSession) -> Item:
    item = session.get(Item, id)

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item

GetItem = Annotated[Item, Depends(get_item)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemBase, session: GetSession, background_tasks: BackgroundTasks) -> Item:
    item = Item.model_validate(item)
    session.add(item)
    session.commit()
    session.refresh(item)
    background_tasks.add_task(send_notification_email, "admin@tienda.com", f"Se agregó el producto {item.name}")

    return item

@router.post("/export")
def export(background_tasks: BackgroundTasks):
    background_tasks.add_task(export_csv)
    return{"message": "La exportación ha comenzado. Te avisaremos cuando termine."}

@router.get("/{id}")
def get_item_by_id(item: GetItem) -> Item:
        return item

@router.get("/")
def get_items(session: GetSession, item_filter: Annotated[FilterItem, Depends()]) -> list[Item]:
    statement = select(Item)

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

    items = session.exec(statement).all()

    return items

@router.patch("/{id}")
def update_item(session: GetSession, item: GetItem, item_data: UpdateItem, background_tasks: BackgroundTasks):


    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)

    if item_data.price is not None:
        background_tasks.add_task(write_audit_log, item.id, item_data.price)

    return item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(session: GetSession, item: GetItem):
    session.delete(item)
    session.commit()

    return None
