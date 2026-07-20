from sqlmodel import Field
from datetime import datetime
from .base import BaseModel
from app.models.enums import ReservationStatus

class Reservation(BaseModel, table=True):
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    reservation_date: datetime
    number_of_people: int
    status: ReservationStatus = Field(default=ReservationStatus.pending, index=True)
