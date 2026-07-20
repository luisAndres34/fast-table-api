from fastapi import APIRouter, status, HTTPException, Depends
import uuid

from app.api.dependencies import SessionDep, CurrentStaff
from app.crud.order import order as crud_order
from app.schemas.order import OrderCreate, OrderPublic, OrderUpdate
from app.services.websocket_manager import ws_manager 

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, session: SessionDep):
    new_order = await crud_order.create(session=session, obj_in=order_in)
    safe_order_json = OrderPublic.model_validate(new_order, from_attributes=True).model_dump(mode="json")
    
    kitchen_message = {
        "event": "new_order",
        "data": safe_order_json
    }
    await ws_manager.broadcast_json(kitchen_message)
    return new_order

@router.get("/pending", response_model=list[OrderPublic])
async def get_pending_orders(session: SessionDep, staff: CurrentStaff):
    orders = await crud_order.get_by_status(session=session, status="pending")
    return orders

@router.patch("/{order_id}/status", response_model=OrderPublic)
async def update_order_status(
    order_id: uuid.UUID, 
    status_update: OrderUpdate, 
    session: SessionDep, 
    staff: CurrentStaff
):
    db_order = await crud_order.get(session=session, id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    updated_order = await crud_order.update_status(
        session=session, 
        db_obj=db_order, 
        new_status=status_update.status
    )
    return updated_order
