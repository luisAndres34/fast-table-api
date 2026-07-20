from sqlmodel import Field, Relationship
from decimal import Decimal
import uuid

from .base import BaseModel

class Dish(BaseModel, table=True):
    name: str
    description: str
    price: Decimal = Field(default=Decimal(0), decimal_places=2, max_digits=10)
    is_available: bool = Field(default=True) 
    category_id: uuid.UUID | None = Field(default=None, foreign_key="category.id")
    category: "Category" = Relationship(back_populates="dishes")
