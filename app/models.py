from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import MetaData

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

SQLModel.metadata = MetaData(naming_convention=naming_convention)

class Token(SQLModel):
    access_token: str
    token_type: str

class UserBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(unique=True)
    role: str = Field(default="user")

class UserCreate(UserBase):
    password: str
    
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

class PublicUser(UserBase):
    id: int

class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: str | None = None

class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    items: list["Item"] = Relationship(back_populates="category")

class CreateCategory(CategoryBase):
    pass

class ItemBase(SQLModel):
    name: str = Field(index=True, unique=True)
    price: int = Field(gt=0)
    stock: int = Field(ge=0)
    

class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    category: Category | None = Relationship(back_populates="items")

class PublicItem(ItemBase):
    id: int
    category: Category | None = None

class CreateItem(ItemBase):
    category_name: str


class UpdateItem(SQLModel):
    name: str | None = Field(default=None)
    price: int | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)

class FilterItem(SQLModel):
    name: str | None = Field(default=None)
    exact_price: int | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    min_price: int | None = Field(default=None, ge=0)
    max_price: int | None = Field(default=None, gt=0)