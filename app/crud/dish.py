from app.crud.base import CRUDBase
from app.models.dish import Dish
from app.schemas.dish import DishCreate, DishUpdate

class CRUDDish(CRUDBase[Dish, DishCreate, DishUpdate]):
    pass

dish = CRUDDish(Dish)
