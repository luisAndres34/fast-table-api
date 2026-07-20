from pydantic import BaseModel
import uuid

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryPublic(CategoryBase):
    id: uuid.UUID

class CategoryUpdate(BaseModel):
    name: str | None = None
