from .dish import DishPublic
from .category import CategoryPublic

class DishPublicWithCategory(DishPublic):
    category: CategoryPublic | None = None

class CategoryPublicWithDishes(CategoryPublic):
    dishes: list[DishPublic] = []
