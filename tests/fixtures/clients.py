import httpx
import pytest_asyncio

@pytest_asyncio.fixture
async def flight_client():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client

@pytest_asyncio.fixture
async def booking_client():
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        yield client

@pytest_asyncio.fixture
async def notification_client():
    async with httpx.AsyncClient(base_url="http://localhost:8002") as client:
        yield client
