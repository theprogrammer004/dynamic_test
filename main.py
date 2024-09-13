from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

# Dictionary to store connected WebSocket clients (ESP32 devices)
connected_clients = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()  # Accept the WebSocket connection
    connected_clients[client_id] = websocket  # Store client connection by ID
    print(f"Client {client_id} connected.")
    
    try:
        while True:
            # Receive data from ESP32
            data = await websocket.receive_text()
            print(f"Message from {client_id}: {data}")
            # Add any additional handling of the incoming message here

    except WebSocketDisconnect:
        # Handle client disconnect
        print(f"Client {client_id} disconnected.")
        connected_clients.pop(client_id, None)

# Function to send data to a specific client (ESP32)
async def send_data_to_client(client_id: str, message: str):
    if client_id in connected_clients:
        websocket = connected_clients[client_id]
        await websocket.send_text(message)
        print(f"Sent data to {client_id}: {message}")
    else:
        print(f"Client {client_id} not connected.")


if __name__ == "__main__":
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
