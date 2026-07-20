import pytest
from httpx import AsyncClient
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, session):
    user_in = UserCreate(
        name="Test User", 
        email="test@example.com", 
        password="password123"
    )
    await crud_user.create(session=session, obj_in=user_in)

    response = await client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, session):
    user_in = UserCreate(name="Test 2", email="wrong@example.com", password="password123")
    await crud_user.create(session=session, obj_in=user_in)

    response = await client.post(
        "/api/v1/login/access-token",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
