from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class SalesSummaryResponse(BaseModel):
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    start_date: datetime | None = None
    end_date: datetime | None = None

class TopDishResponse(BaseModel):
    product_name: str
    total_quantity_sold: int
    total_revenue_generated: Decimal

class ReservationsSummaryResponse(BaseModel):
    total_reservations: int
    pending: int
    confirmed: int
    cancelled: int
    completed: int
