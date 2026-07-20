from pydantic import BaseModel
from datetime import datetime
import uuid

from app.models.enums import OrderStatus

class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    table_number: int
    customer_name: str | None = None
    items: list[OrderItemCreate]

class OrderItemPublic(BaseModel):
    id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: float

class OrderPublic(BaseModel):
    id: uuid.UUID
    table_number: int
    status: OrderStatus
    total_amount: float
    customer_name: str | None
    created_at: datetime
    items: list[OrderItemPublic]

class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
