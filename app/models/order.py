from sqlmodel import Field, Relationship
from typing import List
import uuid

from .base import BaseModel
from app.models.enums import OrderStatus

class OrderItem(BaseModel, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    product_name: str
    quantity: int = Field(default=1)
    unit_price: float
    order: "Order" = Relationship(back_populates="items")

class Order(BaseModel, table=True):
    table_number: int = Field(index=True)
    status: OrderStatus = Field(default=OrderStatus.pending, index=True)
    total_amount: float = Field(default=0.0)
    customer_name: str | None = Field(default=None)
    items: List[OrderItem] = Relationship(
        back_populates="order", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
