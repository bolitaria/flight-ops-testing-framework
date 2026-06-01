import pytest
from tests.fixtures.clients import flight_client

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_flights_returns_200_and_list(flight_client):
    """API test: GET /flights should return 200 and a list."""
    response = await flight_client.get("/flights")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.api
@pytest.mark.asyncio
async def test_create_flight_returns_201(flight_client):
    """API test: POST /flights should create a flight."""
    flight_data = {
        "origin": "MAD",
        "destination": "BCN",
        "departure_time": "10:00",
        "capacity": 100
    }
    response = await flight_client.post("/flights", json=flight_data)
    assert response.status_code == 201
    data = response.json()
    assert data["origin"] == "MAD"
    assert data["available_seats"] == 100
