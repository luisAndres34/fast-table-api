from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager

router = APIRouter()

@router.websocket("/ws/notifications")
async def endpoint_websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Maintain connection alive and listen to incoming frames if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
