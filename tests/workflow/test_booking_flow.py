import pytest
from tests.fixtures.clients import flight_client, booking_client, notification_client

@pytest.mark.workflow
@pytest.mark.asyncio
async def test_full_booking_workflow(flight_client, booking_client, notification_client):
    """End-to-end workflow: flight creation → booking → notification."""
    # 1. Create flight
    flight_data = {
        "origin": "MAD", "destination": "BCN",
        "departure_time": "10:00", "capacity": 10
    }
    response = await flight_client.post("/flights", json=flight_data)
    flight = response.json()

    # 2. Create booking
    booking_data = {"flight_id": flight["id"], "passenger_name": "Test User"}
    response = await booking_client.post("/bookings", json=booking_data)
    booking = response.json()
    assert booking["status"] == "confirmed"

    # 3. Verify notification was sent
    response = await notification_client.get("/notifications")
    notifications = response.json()
    assert any("Test User" in n["recipient"] for n in notifications)
