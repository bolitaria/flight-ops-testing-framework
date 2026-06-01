"""
Notification Service – Consumes booking events from RabbitMQ.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import pika
import json
import threading
import uvicorn

app = FastAPI(title="Notification Service", version="1.0.0")

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/%2F"

class Notification(BaseModel):
    recipient: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)

notifications_db: List[Notification] = []

def consume_events():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='booking_events', durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        notification = Notification(
            recipient=event.get("passenger_name", "unknown"),
            message=f"Booking {event.get('id', '?')} confirmed for flight {event.get('flight_id', '?')}"
        )
        notifications_db.append(notification)
        print(f"Notification saved: {notification.model_dump()}")

    channel.basic_consume(queue='booking_events', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# Start consumer in a separate daemon thread
threading.Thread(target=consume_events, daemon=True).start()

@app.get("/notifications", response_model=List[Notification])
async def get_notifications():
    return notifications_db

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
