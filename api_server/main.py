from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio

app = FastAPI(title="RBIS Analytics API")

# Setup CORS for the React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """
    Manages active websocket connections for real-time broadcasting.
    """
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"status": "RBIS API is running"}

@app.websocket("/ws/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't necessarily expect data from the client,
            # but we need to keep the connection alive.
            data = await websocket.receive_text()
            # If we receive something, we can echo or log it
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/stream/update")
async def post_update(data: dict):
    """
    External vision process posts updates here to be broadcast via websocket.
    """
    message = json.dumps(data)
    await manager.broadcast(message)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
