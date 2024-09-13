import asyncio
import websockets

# Dictionary to store connected clients (ESP32 devices)
connected_clients = {}

async def handler(websocket, path):
    try:
        # Receive client ID from the ESP32 (e.g., "esp32_pot_001")
        client_id = await websocket.recv()
        connected_clients[client_id] = websocket
        print(f"Client {client_id} connected.")
        
        # Keep the connection open and handle incoming messages
        while True:
            message = await websocket.recv()
            print(f"Message from {client_id}: {message}")
            # You can add logic here to respond to messages from the ESP32

    except websockets.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
        del connected_clients[client_id]

# Function to send data to the ESP32
async def send_data_to_client(client_id, data):
    if client_id in connected_clients:
        websocket = connected_clients[client_id]
        await websocket.send(data)
        print(f"Sent data to {client_id}: {data}")
    else:
        print(f"Client {client_id} is not connected.")

# Start the WebSocket server on Render (or any cloud platform)
async def main():
    print("WebSocket server started.")
    async with websockets.serve(handler, "0.0.0.0", 10000):  # Use port 10000 for Render
        await asyncio.Future()  # Run forever

# Run the WebSocket server
asyncio.run(main())
 
