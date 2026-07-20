import pytest
from httpx import AsyncClient
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.models.enums import UserRole

@pytest.mark.asyncio
async def test_menu_operations_as_admin(client: AsyncClient, session):
    admin_in = UserCreate(
        name="Admin User", 
        email="admin@example.com", 
        password="adminpassword", 
        role=UserRole.admin
    )
    await crud_user.create(session=session, obj_in=admin_in)

    login_res = await client.post(
        "/api/v1/login/access-token", 
        data={"username": "admin@example.com", "password": "adminpassword"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cat_payload = {"name": "Italian Food"}
    cat_res = await client.post("/api/v1/categories/", json=cat_payload, headers=headers)
    assert cat_res.status_code == 201
    category_id = cat_res.json()["id"]

    dish_payload = {
        "name": "Pizza Margherita",
        "description": "Classic tomato and mozzarella pizza",
        "price": 10.99,
        "is_available": True,
        "category_id": category_id
    }
    dish_res = await client.post("/api/v1/dishes/", json=dish_payload, headers=headers)
    assert dish_res.status_code == 201
    assert dish_res.json()["name"] == "Pizza Margherita"

    get_res = await client.get("/api/v1/dishes/")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1
