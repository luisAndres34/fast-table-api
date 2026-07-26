from decimal import Decimal
from sqlmodel import Field, Relationship
from typing import List
import uuid

from .base import BaseModel
from app.models.enums import OrderStatus

class OrderItem(BaseModel, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    product_name: str
    quantity: int = Field(default=1)
    unit_price: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    order: "Order" = Relationship(back_populates="items")

class Order(BaseModel, table=True):
    table_number: int = Field(index=True)
    status: OrderStatus = Field(default=OrderStatus.pending, index=True)
    total_amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    customer_name: str | None = Field(default=None)
    items: List[OrderItem] = Relationship(
        back_populates="order", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    payments: List["Payment"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin"}
    )