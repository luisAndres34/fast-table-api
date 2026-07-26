from decimal import Decimal
from sqlmodel import Field, Relationship
import uuid

from .base import BaseModel
from app.models.enums import PaymentStatus

class Payment(BaseModel, table=True):
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    stripe_session_id: str | None = Field(default=None, index=True)
    stripe_payment_intent_id: str | None = Field(default=None, index=True)
    amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=10)
    currency: str = Field(default="usd")
    status: PaymentStatus = Field(default=PaymentStatus.pending, index=True)
    customer_email: str | None = Field(default=None)

    order: "Order" = Relationship(back_populates="payments")