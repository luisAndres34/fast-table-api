import pytest
from httpx import AsyncClient
from app.crud.user import user as crud_user
from app.crud.order import order as crud_order
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.models.enums import UserRole, OrderStatus

async def get_auth_header(client: AsyncClient, session, role: UserRole) -> dict[str, str]:
    email = f"user_{role.value}@example.com"
    password = "password123"
    user_in = UserCreate(name="Test User", email=email, password=password, role=role)
    await crud_user.create(session=session, obj_in=user_in)

    response = await client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_analytics_rbac_forbidden_for_client(client: AsyncClient, session):
    headers = await get_auth_header(client, session, role=UserRole.client)
    
    response = await client.get("/api/v1/analytics/sales", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"


@pytest.mark.asyncio
async def test_analytics_sales_summary_as_admin(client: AsyncClient, session):
    headers = await get_auth_header(client, session, role=UserRole.admin)

    # Create 2 paid orders
    order1 = await crud_order.create(session, obj_in=OrderCreate(
        table_number=1,
        items=[OrderItemCreate(product_name="Burger", quantity=2, unit_price=10.00)] # Total $20.00
    ))
    await crud_order.update_status(session, db_obj=order1, new_status=OrderStatus.paid)

    order2 = await crud_order.create(session, obj_in=OrderCreate(
        table_number=2,
        items=[OrderItemCreate(product_name="Fries", quantity=1, unit_price=5.00)] # Total $5.00
    ))
    await crud_order.update_status(session, db_obj=order2, new_status=OrderStatus.paid)

    response = await client.get("/api/v1/analytics/sales", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == "25.00"
    assert data["total_orders"] == 2
    assert data["average_order_value"] == "12.50"


@pytest.mark.asyncio
async def test_analytics_top_dishes_as_admin(client: AsyncClient, session):
    headers = await get_auth_header(client, session, role=UserRole.admin)

    # Order 1: 5 Tacos
    order1 = await crud_order.create(session, obj_in=OrderCreate(
        table_number=1,
        items=[OrderItemCreate(product_name="Tacos", quantity=5, unit_price=2.00)]
    ))
    await crud_order.update_status(session, db_obj=order1, new_status=OrderStatus.paid)

    # Order 2: 1 Soda, 2 Tacos
    order2 = await crud_order.create(session, obj_in=OrderCreate(
        table_number=2,
        items=[
            OrderItemCreate(product_name="Soda", quantity=1, unit_price=1.50),
            OrderItemCreate(product_name="Tacos", quantity=2, unit_price=2.00)
        ]
    ))
    await crud_order.update_status(session, db_obj=order2, new_status=OrderStatus.paid)

    response = await client.get("/api/v1/analytics/top-dishes?limit=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    # First item should be Tacos (Total quantity 7)
    assert data[0]["product_name"] == "Tacos"
    assert data[0]["total_quantity_sold"] == 7
    assert data[0]["total_revenue_generated"] == "14.00"
