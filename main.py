from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <button onclick="connectWebSocket()">Connect</button>
        <script>
            function connectWebSocket() {
                const ws = new WebSocket("wss://your-render-app-url.onrender.com/ws");
                ws.onopen = function() {
                    console.log("WebSocket connection opened");
                };
                ws.onmessage = function(event) {
                    console.log("Message from server: ", event.data);
                };
                ws.onclose = function() {
                    console.log("WebSocket connection closed");
                };
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
