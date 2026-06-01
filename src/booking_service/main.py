"""
Booking Service – Manages flight reservations.
Integrates with Flight Service and triggers notifications.
Implements retry logic and timeout handling for robustness.
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import uvicorn
import asyncio

app = FastAPI(title="Booking Service", version="1.0.0")

FLIGHT_SERVICE_URL = "http://flight_service:8000"
NOTIFICATION_SERVICE_URL = "http://notification_service:8002"

class Booking(BaseModel):
    id: Optional[int] = None
    flight_id: int
    passenger_name: str = Field(..., min_length=1)
    status: str = "confirmed"

bookings_db: List[Booking] = []

async def call_external_api(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    """Utility for external API calls with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.request(method, url, timeout=5.0, **kwargs)
            return response
        except httpx.RequestError as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"External service unavailable: {str(e)}"
                )
            await asyncio.sleep(2 ** attempt)  # exponential backoff
    raise HTTPException(status_code=500, detail="Unexpected error in external call")

@app.get("/bookings", response_model=List[Booking])
async def get_bookings():
    return bookings_db

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    for booking in bookings_db:
        if booking.id == booking_id:
            return booking
    raise HTTPException(status_code=404, detail="Booking not found")

@app.post("/bookings", status_code=status.HTTP_201_CREATED, response_model=Booking)
async def create_booking(booking: Booking):
    async with httpx.AsyncClient() as client:
        # Check flight exists and has seats
        flight_response = await call_external_api(
            client, "GET", f"{FLIGHT_SERVICE_URL}/flights/{booking.flight_id}"
        )
        if flight_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        book_response = await call_external_api(
            client, "PUT", f"{FLIGHT_SERVICE_URL}/flights/{booking.flight_id}/book"
        )
        if book_response.status_code == 409:
            raise HTTPException(status_code=409, detail="No available seats")
    
    booking.id = len(bookings_db) + 1
    bookings_db.append(booking)
    
    # Notify passenger asynchronously – fire-and-forget for demo purposes
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notify",
                json={"recipient": booking.passenger_name, "message": f"Booking confirmed for flight {booking.flight_id}"},
                timeout=3.0
            )
        except Exception:
            # Notification failure should not block booking
            pass
    
    return booking

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
