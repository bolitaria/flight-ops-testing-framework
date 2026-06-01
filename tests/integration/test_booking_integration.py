import pytest
import asyncio
from tests.fixtures.clients import flight_client, booking_client, notification_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_booking_calls_flight_service(flight_client, booking_client, notification_client):
    flight_data = {"origin":"MAD","destination":"BCN","departure_time":"10:00","capacity":10}
    response = await flight_client.post("/flights", json=flight_data)
    flight = response.json()

    booking_data = {"flight_id": flight["id"], "passenger_name": "Test User"}
    response = await booking_client.post("/bookings", json=booking_data)
    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"

    # Wait for async notification with polling
    timeout = 15
    start = asyncio.get_event_loop().time()
    while True:
        response = await notification_client.get("/notifications")
        notifications = response.json()
        if any("Test User" in n["recipient"] for n in notifications):
            break
        if asyncio.get_event_loop().time() - start > timeout:
            pytest.fail("Notification not received within timeout")
        await asyncio.sleep(1)
