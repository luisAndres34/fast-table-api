from fastapi import APIRouter

from . import auth, users, ws_notifications, orders, reservations, category, dish, payments, analytics

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(ws_notifications.router)
api_router.include_router(orders.router)
api_router.include_router(reservations.router)
api_router.include_router(category.router)
api_router.include_router(dish.router)
api_router.include_router(payments.router)
api_router.include_router(analytics.router)
