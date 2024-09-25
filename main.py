import base64
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from starlette.websockets import WebSocketDisconnect

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected WebSocket clients
clients = []

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    logging.info("WebSocket connection established")

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received message: {data}")

            # Process received message (could be text or control commands)
            if data.startswith("TEXT:"):
                # Broadcast the text message to all clients
                text_message = data[5:]  # Strip "TEXT:" prefix
                await broadcast_text_message(text_message)
            else:
                logging.info(f"Received unknown message: {data}")

    except WebSocketDisconnect:
        clients.remove(websocket)
        logging.info("WebSocket connection closed")

# Broadcast text message to all connected WebSocket clients
async def broadcast_text_message(message: str):
    for client in clients:
        await client.send_text(f"TEXT:{message}")

# Send image chunks to WebSocket clients
async def send_image_chunks(image_data: bytes, chunk_size: int = 2048):
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # Send the image in chunks to prevent WebSocket disconnection
    for i in range(0, len(encoded_image), chunk_size):
        chunk = encoded_image[i:i + chunk_size]
        message = f"IMAGE_CHUNK:{chunk}"

        for client in clients:
            await client.send_text(message)
        await asyncio.sleep(0.1)  # Prevent overwhelming the client

    # Send a final message to indicate the end of the image
    for client in clients:
        await client.send_text("IMAGE_DONE")

# Endpoint to send a JPEG image
@app.post("/send_image/")
async def send_image(file: UploadFile = File(...)):
    image_data = await file.read()
    await send_image_chunks(image_data)
    return {"status": "Image sent in chunks"}

# Endpoint to broadcast a text message (HTTP POST)
@app.post("/send_message/")
async def send_message(message: str):
    await broadcast_text_message(message)
    return {"status": "Message sent"}

# Run FastAPI server with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
