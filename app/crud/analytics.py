from datetime import datetime
from decimal import Decimal
from sqlmodel import select
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.reservation import Reservation
from app.models.enums import OrderStatus, ReservationStatus
from app.schemas.analytics import SalesSummaryResponse, TopDishResponse, ReservationsSummaryResponse

class CRUDAnalytics:

    async def get_sales_summary(
        self, 
        session: AsyncSession, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None
    ) -> SalesSummaryResponse:
        """
        Computes total sales, paid order count, and average order value using SQL aggregation.
        """
        statement = select(
            func.coalesce(func.sum(Order.total_amount), Decimal("0.00")).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.avg(Order.total_amount), Decimal("0.00")).label("average_order_value")
        ).where(Order.status == OrderStatus.paid)

        if start_date:
            statement = statement.where(Order.created_at >= start_date)
        if end_date:
            statement = statement.where(Order.created_at <= end_date)

        result = await session.execute(statement)
        row = result.one()

        # Format Decimals strictly to 2 decimal places (.quantize)
        total_rev = Decimal(str(row.total_revenue)).quantize(Decimal("0.01"))
        avg_val = Decimal(str(row.average_order_value)).quantize(Decimal("0.01"))

        return SalesSummaryResponse(
            total_revenue=total_rev,
            total_orders=row.total_orders,
            average_order_value=avg_val,
            start_date=start_date,
            end_date=end_date
        )

    async def get_top_dishes(
        self, 
        session: AsyncSession, 
        limit: int = 5,
        start_date: datetime | None = None, 
        end_date: datetime | None = None
    ) -> list[TopDishResponse]:
        """
        Retrieves the top N best-selling dishes using GROUP BY and SUM aggregations.
        """
        statement = (
            select(
                OrderItem.product_name,
                func.sum(OrderItem.quantity).label("total_quantity"),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue")
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.status == OrderStatus.paid)
            .group_by(OrderItem.product_name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )

        if start_date:
            statement = statement.where(Order.created_at >= start_date)
        if end_date:
            statement = statement.where(Order.created_at <= end_date)

        result = await session.execute(statement)
        rows = result.all()

        top_dishes = [
            TopDishResponse(
                product_name=row.product_name,
                total_quantity_sold=row.total_quantity,
                total_revenue_generated=Decimal(str(row.total_revenue))
            )
            for row in rows
        ]

        return top_dishes

    async def get_reservations_summary(self, session: AsyncSession) -> ReservationsSummaryResponse:
        """
        Computes table reservation metrics grouped by reservation status.
        """
        statement = select(
            func.count(Reservation.id).label("total"),
            func.count(Reservation.id).filter(Reservation.status == ReservationStatus.pending).label("pending"),
            func.count(Reservation.id).filter(Reservation.status == ReservationStatus.confirmed).label("confirmed"),
            func.count(Reservation.id).filter(Reservation.status == ReservationStatus.cancelled).label("cancelled"),
            func.count(Reservation.id).filter(Reservation.status == ReservationStatus.completed).label("completed"),
        )

        result = await session.execute(statement)
        row = result.one()

        return ReservationsSummaryResponse(
            total_reservations=row.total,
            pending=row.pending,
            confirmed=row.confirmed,
            cancelled=row.cancelled,
            completed=row.completed
        )

analytics = CRUDAnalytics()
