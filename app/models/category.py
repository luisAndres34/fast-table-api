from sqlmodel import Field, Relationship
from .base import BaseModel

class Category(BaseModel, table=True):
    name: str
    dishes: list["Dish"] = Relationship(back_populates="category")
