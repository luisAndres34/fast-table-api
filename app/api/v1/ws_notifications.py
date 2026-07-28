from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager
from app.core.logger import logger

router = APIRouter()

@router.websocket("/ws/notifications")
async def endpoint_websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)
