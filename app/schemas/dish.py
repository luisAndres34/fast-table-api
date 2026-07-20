from decimal import Decimal
from pydantic import BaseModel
import uuid

class DishBase(BaseModel):
    name: str
    description: str
    price: Decimal
    is_available: bool = True
    category_id: uuid.UUID | None = None

class DishCreate(DishBase):
    pass

class DishPublic(DishBase):
    id: uuid.UUID

class DishUpdate(BaseModel):
    name: None | str = None
    description: None | str = None
    price: None | Decimal = None
    category_id: uuid.UUID | None = None
