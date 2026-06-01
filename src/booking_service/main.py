"""
Booking Service – Manages flight reservations.
Publishes events to RabbitMQ instead of direct HTTP calls.
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import pika
import json
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Booking Service", version="1.0.0")
Instrumentator().instrument(app).expose(app)

FLIGHT_SERVICE_URL = "http://flight_service:8000"
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/%2F"

class Booking(BaseModel):
    id: Optional[int] = None
    flight_id: int
    passenger_name: str = Field(..., min_length=1)
    status: str = "confirmed"

bookings_db: List[Booking] = []

def publish_event(booking: Booking):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='booking_events', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='booking_events',
        body=json.dumps(booking.model_dump()),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

@app.get("/bookings", response_model=List[Booking])
async def get_bookings():
    return bookings_db

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    for booking in bookings_db:
        if booking.id == booking_id:
            return booking
    raise HTTPException(status_code=404, detail="Booking not found")

@app.post("/bookings", status_code=201, response_model=Booking)
async def create_booking(booking: Booking):
    async with httpx.AsyncClient() as client:
        flight_response = await client.get(f"{FLIGHT_SERVICE_URL}/flights/{booking.flight_id}")
        if flight_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Flight not found")
        book_response = await client.put(f"{FLIGHT_SERVICE_URL}/flights/{booking.flight_id}/book")
        if book_response.status_code == 409:
            raise HTTPException(status_code=409, detail="No available seats")
    booking.id = len(bookings_db) + 1
    bookings_db.append(booking)
    publish_event(booking)
    return booking

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
