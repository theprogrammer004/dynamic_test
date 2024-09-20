from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# CORS settings to allow all origins (for testing purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you may want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Store connected WebSocket clients
clients = []

# Model for message data
class Message(BaseModel):
    message: str

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        clients.append(websocket)
        logging.info("WebSocket connection established")
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            logging.info(f"Received message: {data}")
            
            # Send a response back to the client
            response = f"Message received: {data}"
            await websocket.send_text(response)
    except Exception as e:
        logging.error(f"WebSocket connection error: {e}")
    finally:
        clients.remove(websocket)
        logging.info("WebSocket connection closed")

# Endpoint to send a message to all connected clients
@app.post("/send")
async def send_message(message: Message):
    for client in clients:
        await client.send_text(message.message)
    return {"status": "Message sent"}

# New API endpoint to send an image to connected WebSocket clients
@app.post("/send_image/")
async def send_image(file: UploadFile = File(...)):
    # Read the image file
    image_data = await file.read()

    # Encode the image to base64
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # Send the encoded image to all connected WebSocket clients
    for client in clients:
        await client.send_text(f"IMAGE:{encoded_image}")

    return {"status": "Image sent to all clients"}    

# Run FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
