from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Global variable to store the message
message_to_display = "Welcome to TFT!"

# Define the data structure for the POST request
class MessageData(BaseModel):
    data: str

# Route to change the message
@app.post("/send_data/")
async def send_data(message: MessageData):
    global message_to_display
    message_to_display = message.data
    return {"status": "success", "message": "Message updated successfully"}

# Route to fetch the current message
@app.get("/get_data/")
async def get_data():
    return {"message": message_to_display}

# Optional: Root endpoint to verify the API is running
@app.get("/")
async def root():
    return {"status": "FastAPI server running"}
