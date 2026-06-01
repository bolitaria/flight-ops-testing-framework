import pytest
from tests.fixtures.clients import flight_client, booking_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_calls_flight_service(flight_client, booking_client):
    """Integration test: booking creation should interact with flight service."""
    # Create a flight
    flight_data = {
        "origin": "MAD", "destination": "BCN",
        "departure_time": "10:00", "capacity": 10
    }
    response = await flight_client.post("/flights", json=flight_data)
    flight = response.json()

    # Create a booking
    booking_data = {"flight_id": flight["id"], "passenger_name": "Test User"}
    response = await booking_client.post("/bookings", json=booking_data)
    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"
