from fastapi import APIRouter, Query
from datetime import datetime

from app.api.dependencies import SessionDep, CurrentAdmin
from app.crud.analytics import analytics as crud_analytics
from app.schemas.analytics import SalesSummaryResponse, TopDishResponse, ReservationsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/sales", response_model=SalesSummaryResponse)
async def get_sales_summary(
    session: SessionDep,
    admin: CurrentAdmin,
    start_date: datetime | None = Query(None, description="Start date filter (e.g. 2026-01-01T00:00:00)"),
    end_date: datetime | None = Query(None, description="End date filter (e.g. 2026-12-31T23:59:59)")
):
    """
    Retrieve total sales, paid order counts, and average order value within a date range.
    (Admin privileges required).
    """
    return await crud_analytics.get_sales_summary(
        session=session, 
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/top-dishes", response_model=list[TopDishResponse])
async def get_top_dishes(
    session: SessionDep,
    admin: CurrentAdmin,
    limit: int = Query(5, ge=1, le=20, description="Number of top selling dishes to return"),
    start_date: datetime | None = Query(None, description="Start date filter"),
    end_date: datetime | None = Query(None, description="End date filter")
):
    """
    Retrieve the top best-selling dishes ranked by units sold.
    (Admin privileges required).
    """
    return await crud_analytics.get_top_dishes(
        session=session, 
        limit=limit, 
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/reservations", response_model=ReservationsSummaryResponse)
async def get_reservations_summary(
    session: SessionDep,
    admin: CurrentAdmin
):
    """
    Retrieve table reservation metrics grouped by status.
    (Admin privileges required).
    """
    return await crud_analytics.get_reservations_summary(session=session)
