"""
Flight Service – Core API for flight management.
This microservice demonstrates:
- Clean REST API with FastAPI
- Input validation with Pydantic
- In‑memory data store (simulating a database)
- Separation of concerns for easy testing
In production, this would use a real database, authentication, and persistent storage.
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Flight Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class Flight(BaseModel):
    id: Optional[int] = None
    origin: str = Field(..., min_length=3, max_length=3, description="IATA code")
    destination: str = Field(..., min_length=3, max_length=3)
    departure_time: str
    capacity: int = Field(..., gt=0)
    available_seats: int = 0

flights_db: List[Flight] = []

@app.get("/flights", response_model=List[Flight])
async def get_flights():
    """Retrieve all flights."""
    return flights_db

@app.get("/flights/{flight_id}", response_model=Flight)
async def get_flight(flight_id: int):
    """Retrieve a single flight by ID."""
    for flight in flights_db:
        if flight.id == flight_id:
            return flight
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Flight not found"
    )

@app.post("/flights", status_code=status.HTTP_201_CREATED, response_model=Flight)
async def create_flight(flight: Flight):
    """Create a new flight."""
    flight.id = len(flights_db) + 1
    flight.available_seats = flight.capacity
    flights_db.append(flight)
    return flight

@app.put("/flights/{flight_id}/book")
async def book_seat(flight_id: int):
    """Book a seat – decreases available seats."""
    for flight in flights_db:
        if flight.id == flight_id:
            if flight.available_seats > 0:
                flight.available_seats -= 1
                return {
                    "message": "Seat booked",
                    "available_seats": flight.available_seats
                }
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No available seats"
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Flight not found"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
