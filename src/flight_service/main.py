"""
Flight Service – Core API for flight management.
Uses PostgreSQL via SQLAlchemy. Exposes Prometheus metrics.
"""
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import models
from database import engine, SessionLocal
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Flight Service", version="1.0.0", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

class FlightCreate(BaseModel):
    origin: str
    destination: str
    departure_time: str
    capacity: int

class FlightResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_time: str
    capacity: int
    available_seats: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/flights", response_model=List[FlightResponse])
async def get_flights(db: Session = Depends(get_db)):
    return db.query(models.Flight).all()

@app.get("/flights/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@app.post("/flights", status_code=201, response_model=FlightResponse)
async def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    db_flight = models.Flight(
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time,
        capacity=flight.capacity,
        available_seats=flight.capacity
    )
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

@app.put("/flights/{flight_id}/book")
async def book_seat(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    if flight.available_seats <= 0:
        raise HTTPException(status_code=409, detail="No available seats")
    flight.available_seats -= 1
    db.commit()
    return {"message": "Seat booked", "available_seats": flight.available_seats}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
