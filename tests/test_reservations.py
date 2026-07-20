import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_reservation_success(client: AsyncClient):
    # Arrange: Build valid reservation payload
    payload = {
        "customer_name": "John Doe",
        "customer_email": "johndoe@example.com",
        "customer_phone": "123-456-7890",
        "reservation_date": "2026-07-15T20:00:00",
        "number_of_people": 4
    }

    # Act: Send post request to the endpoint
    response = await client.post("/api/v1/reservations/", json=payload)

    # Assert: Confirm response values and persistence
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["customer_email"] == "johndoe@example.com"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_reservation_invalid_email(client: AsyncClient):
    # Arrange: Build invalid reservation payload with a bad email
    payload = {
        "customer_name": "John Doe",
        "customer_email": "not-an-email",
        "customer_phone": "123-456-7890",
        "reservation_date": "2026-07-15T20:00:00",
        "number_of_people": 4
    }

    # Act: Send post request to the endpoint
    response = await client.post("/api/v1/reservations/", json=payload)

    # Assert: Confirm Pydantic validation fails with 422 Unprocessable Entity
    assert response.status_code == 422
