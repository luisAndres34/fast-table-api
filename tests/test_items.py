from httpx import AsyncClient
from fastapi import status
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_create_item_no_auth(client: AsyncClient):
   response = await client.post("/items/", json={"name": "Item Robado", "price": 50, "stock": 100})

   assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
   user_data = {"name": "Luis", "email": "andreslph3@gmail.com", "password": "Luis123"}
   user_response = await client.post("/users/", json=user_data)

   assert user_response.status_code == status.HTTP_201_CREATED

   login_data = {"username": "andreslph3@gmail.com", "password": "Luis123"}
   login_response = await client.post("/users/token", data=login_data)

   assert login_response.status_code == status.HTTP_200_OK

   token = login_response.json()["access_token"]
   return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_item(client: AsyncClient, auth_headers):
   item_data = {"name": "Manzana", "price": 5, "stock": 10}
   response = await client.post("/items/", json=item_data, headers=auth_headers)
    
   assert response.status_code == status.HTTP_201_CREATED
   assert response.json()["name"] == "Manzana"

   return response.json()

@pytest.mark.asyncio
async def test_get_item(client: AsyncClient, auth_headers, sample_item):
   item_id = sample_item["id"]
   response = await client.get(f"/items/{item_id}", headers=auth_headers)
   assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_invalid_item_id(client: AsyncClient, auth_headers):
   item_id = 0
   response = await client.get(f"/items/{item_id}", headers=auth_headers)
   assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, auth_headers, sample_item):
   item_id = sample_item["id"]
   response = await client.patch(f"/items/{item_id}", json={"name": "Naranja", "price": 7, "stock": 0},  headers=auth_headers)

   assert response.status_code == status.HTTP_200_OK
   assert response.json()["name"] == "Naranja"

@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, auth_headers, sample_item):
   item_id = sample_item["id"]
   response = await client.delete(f"/items/{item_id}", headers=auth_headers)

   assert response.status_code == status.HTTP_204_NO_CONTENT
