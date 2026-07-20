import pytest
from httpx import AsyncClient
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.models.enums import UserRole

@pytest.mark.asyncio
async def test_create_user_public(client: AsyncClient):
    payload = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "supersecretpassword"
    }
    
    response = await client.post("/api/v1/users/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data

@pytest.mark.asyncio
async def test_get_users_as_admin(client: AsyncClient, session):
    admin_in = UserCreate(
        name="Admin", 
        email="admin@example.com", 
        password="adminpass", 
        role=UserRole.admin
    )
    await crud_user.create(session=session, obj_in=admin_in)

    login_res = await client.post(
        "/api/v1/login/access-token", 
        data={"username": "admin@example.com", "password": "adminpass"}
    )
    token = login_res.json()["access_token"]

    response = await client.get(
        "/api/v1/users/", 
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_users_as_normal_user_forbidden(client: AsyncClient, session):
    user_in = UserCreate(
        name="Normal", 
        email="normal@example.com", 
        password="userpass", 
        role=UserRole.client
    )
    await crud_user.create(session=session, obj_in=user_in)

    login_res = await client.post(
        "/api/v1/login/access-token", 
        data={"username": "normal@example.com", "password": "userpass"}
    )
    token = login_res.json()["access_token"]

    response = await client.get(
        "/api/v1/users/", 
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"
