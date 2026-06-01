"""
Notification Service – Consumes booking events from RabbitMQ.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import pika
import json
import threading
import time
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Notification Service", version="1.0.0")
Instrumentator().instrument(app).expose(app)

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/%2F"

class Notification(BaseModel):
    recipient: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)

notifications_db: List[Notification] = []

def consume_events():
    # Wait until RabbitMQ is ready, retrying connection
    while True:
        try:
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
            print("Notification consumer connected to RabbitMQ, waiting for messages...")
            channel.start_consuming()
            break  # if start_consuming returns, we exit the loop
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready yet, retrying in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"Unexpected error in consumer: {e}. Retrying in 5 seconds...")
            time.sleep(5)

threading.Thread(target=consume_events, daemon=True).start()

@app.get("/notifications", response_model=List[Notification])
async def get_notifications():
    return notifications_db

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
