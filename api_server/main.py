from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api_server.database import SessionLocal, init_db, BehaviorEvent, EngagementMetric


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RBIS Analytics API", lifespan=lifespan)

# Setup CORS for the React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PersonUpdate(BaseModel):
    id: int
    bbox: list[float] = Field(default_factory=list)
    events: list[str] = Field(default_factory=list)
    engagement_score: float


class FrameUpdate(BaseModel):
    frame_id: int
    persons: list[PersonUpdate] = Field(default_factory=list)


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
        # A socket can be dropped by broadcast() and again by its own handler.
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)
        for connection in dead_connections:
            self.disconnect(connection)

manager = ConnectionManager()


def persist_frame(update: FrameUpdate):
    """
    Blocking DB write; run it off the event loop.
    """
    db = SessionLocal()
    try:
        for person in update.persons:
            for event_type in person.events:
                db.add(BehaviorEvent(
                    person_id=person.id,
                    event_type=event_type,
                    confidence=1.0,
                ))
            db.add(EngagementMetric(
                person_id=person.id,
                engagement_score=person.engagement_score,
            ))
        db.commit()
    finally:
        db.close()


@app.get("/")
async def root():
    return {"status": "RBIS API is running"}

@app.websocket("/ws/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect data from the client, but we need to
            # keep reading so a disconnect is noticed.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/stream/update")
async def post_update(update: FrameUpdate):
    """
    External vision process posts updates here to be broadcast via websocket.
    """
    await run_in_threadpool(persist_frame, update)
    await manager.broadcast(update.model_dump_json())
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
