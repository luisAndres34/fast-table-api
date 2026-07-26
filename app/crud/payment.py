from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.crud.base import CRUDBase
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.models.enums import PaymentStatus

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):

    async def get_by_stripe_session_id(self, session: AsyncSession, session_id: str) -> Payment | None:
        statement = select(self.model).where(self.model.stripe_session_id == session_id)
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_by_order_id(self, session: AsyncSession, order_id: uuid.UUID) -> list[Payment]:
        statement = select(self.model).where(self.model.order_id == order_id)
        result = await session.execute(statement)
        return result.scalars().all()

    async def update_status(
        self, 
        session: AsyncSession, 
        db_obj: Payment, 
        new_status: PaymentStatus,
        payment_intent_id: str | None = None
    ) -> Payment:
        db_obj.status = new_status
        if payment_intent_id:
            db_obj.stripe_payment_intent_id = payment_intent_id
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

payment = CRUDPayment(Payment)