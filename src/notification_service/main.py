"""
Notification Service – Simulates sending notifications.
Keeps a record of all sent notifications for verification.
"""
from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from typing import List
import uvicorn

app = FastAPI(title="Notification Service", version="1.0.0")

class Notification(BaseModel):
    recipient: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)

notifications_db: List[Notification] = []

@app.post("/notify", status_code=status.HTTP_200_OK)
async def send_notification(notification: Notification):
    """Simulate sending a notification."""
    notifications_db.append(notification)
    return {"status": "sent", "recipient": notification.recipient}

@app.get("/notifications", response_model=List[Notification])
async def get_notifications():
    """Retrieve all sent notifications."""
    return notifications_db

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
