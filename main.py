from fastapi import FastAPI, WebSocket, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from starlette.websockets import WebSocketDisconnect

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
    await websocket.accept()
    clients.append(websocket)
    logging.info("WebSocket connection established")

    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            logging.info(f"Received message: {data}")
            
            # Send a response back to the client
            response = f"Message received: {data}"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        logging.info("WebSocket connection closed")
    except Exception as e:
        logging.error(f"WebSocket connection error: {e}")
    finally:
        clients.remove(websocket)

# Endpoint to send a message to all connected clients
@app.post("/send")
async def send_message(message: Message):
    for client in clients:
        try:
            await client.send_text(message.message)
        except Exception as e:
            logging.error(f"Error sending message to client: {e}")
    return {"status": "Message sent"}

# Endpoint to send an image to connected WebSocket clients
@app.post("/send_image/")
async def send_image(file: UploadFile = File(...)):
    # Read the image file
    image_data = await file.read()

    # Send the image data as binary to all connected WebSocket clients
    disconnected_clients = []
    for client in clients:
        try:
            await client.send_bytes(image_data)
            logging.info("Image sent to client")
        except Exception as e:
            logging.error(f"Error sending image to client: {e}")
            disconnected_clients.append(client)

    # Remove disconnected clients from the list
    for client in disconnected_clients:
        clients.remove(client)

    return {"status": "Image sent to all connected clients"}

# Run FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    # You can set a larger request size limit using uvicorn (example: 10 MB)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", limit_max_request_size=10 * 1024 * 1024)
