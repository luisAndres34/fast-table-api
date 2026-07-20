from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.models.enums import ReservationStatus

class ReservationCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str | None = None
    reservation_date: datetime
    number_of_people: int

class ReservationPublic(ReservationCreate):
    id: uuid.UUID
    status: ReservationStatus
