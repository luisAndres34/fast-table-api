from decimal import Decimal
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.models.enums import PaymentStatus

class PaymentBase(BaseModel):
    order_id: uuid.UUID
    amount: Decimal
    currency: str = "usd"
    customer_email: EmailStr | None = None

class PaymentCreate(PaymentBase):
    stripe_session_id: str | None = None

class PaymentUpdate(BaseModel):
    status: PaymentStatus | None = None
    stripe_payment_intent_id: str | None = None
    customer_email: EmailStr | None = None

class PaymentPublic(PaymentBase):
    id: uuid.UUID
    stripe_session_id: str | None = None
    stripe_payment_intent_id: str | None = None
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

class CreateCheckoutSessionRequest(BaseModel):
    order_id: uuid.UUID
    customer_email: EmailStr | None = None
    success_url: str = "http://localhost:3000/payment/success?session_id={CHECKOUT_SESSION_ID}"
    cancel_url: str = "http://localhost:3000/payment/cancel"

class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str