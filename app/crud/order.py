from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate
from app.models.enums import OrderStatus

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):

    async def create(self, session: AsyncSession, obj_in: OrderCreate) -> Order:
        total = sum(item.quantity * item.unit_price for item in obj_in.items)
        
        db_order = Order(
            table_number=obj_in.table_number,
            customer_name=obj_in.customer_name,
            total_amount=total,
            status=OrderStatus.pending
        )
        session.add(db_order)
        
        try:
            await session.flush() 
            
            for item in obj_in.items:
                db_item = OrderItem(
                    order_id=db_order.id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                session.add(db_item)
                
            await session.commit()
            await session.refresh(db_order)
            return db_order
            
        except Exception as e:
            await session.rollback()
            raise e

    async def get_by_status(self, session: AsyncSession, status: str) -> list[Order]:
        statement = select(self.model).where(self.model.status == status)
        result = await session.execute(statement)
        return result.scalars().all()

    async def update_status(self, session: AsyncSession, db_obj: Order, new_status: str) -> Order:
        db_obj.status = new_status
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

order = CRUDOrder(Order)
