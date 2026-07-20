import pytest
from httpx import AsyncClient
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.models.enums import UserRole

@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient, session):
    payload = {
        "table_number": 5,
        "customer_name": "Alice",
        "items": [
            {"product_name": "Tacos", "quantity": 3, "unit_price": 2.50},
            {"product_name": "Soda", "quantity": 2, "unit_price": 1.50}
        ]
    }

    response = await client.post("/api/v1/orders/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["table_number"] == 5
    assert data["status"] == "pending"
    assert data["total_amount"] == 10.50
    assert len(data["items"]) == 2
    assert "id" in data

@pytest.mark.asyncio
async def test_get_pending_orders_and_update_status(client: AsyncClient, session):
    waiter_in = UserCreate(
        name="Waiter Joe", 
        email="waiter@example.com", 
        password="waiterpassword", 
        role=UserRole.waiter
    )
    await crud_user.create(session=session, obj_in=waiter_in)

    order_payload = {
        "table_number": 12,
        "items": [{"product_name": "Burger", "quantity": 1, "unit_price": 8.00}]
    }
    order_res = await client.post("/api/v1/orders/", json=order_payload)
    order_id = order_res.json()["id"]

    login_res = await client.post(
        "/api/v1/login/access-token", 
        data={"username": "waiter@example.com", "password": "waiterpassword"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pending_res = await client.get("/api/v1/orders/pending", headers=headers)
    assert pending_res.status_code == 200
    assert len(pending_res.json()) >= 1

    update_payload = {"status": "preparing"}
    update_res = await client.patch(
        f"/api/v1/orders/{order_id}/status", 
        json=update_payload, 
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "preparing"
