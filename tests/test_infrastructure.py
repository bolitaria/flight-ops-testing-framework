import pytest
import httpx

@pytest.mark.infra
@pytest.mark.asyncio
async def test_prometheus_targets_are_up():
    """Verify that all three services are being scraped by Prometheus."""
    async with httpx.AsyncClient(base_url="http://localhost:9090") as client:
        response = await client.get("/api/v1/targets")
        assert response.status_code == 200
        targets = response.json()["data"]["activeTargets"]
        up_services = {t["labels"]["job"] for t in targets if t["health"] == "up"}
        expected = {"flight_service", "booking_service", "notification_service"}
        assert up_services == expected
