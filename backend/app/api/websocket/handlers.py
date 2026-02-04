from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.infrastructure.messaging.websocket_manager import connection_manager
from app.utils.null_check import Util
import json

router = APIRouter()


@router.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await connection_manager.connect(websocket, "admin")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "admin")


@router.websocket("/ws/kiosk/{device_id}")
async def kiosk_websocket(websocket: WebSocket, device_id: str):
    await connection_manager.connect(websocket, "kiosk", device_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "order_status_request":
                order_id = message.get("order_id")
                if Util.is_not_empty(order_id):
                    await websocket.send_json({
                        "type": "order_status_request_received",
                        "order_id": order_id
                    })
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "kiosk", device_id)


@router.websocket("/ws/voice/{session_id}")
async def voice_assistant_websocket(websocket: WebSocket, session_id: str):
    await connection_manager.connect(websocket, f"voice_{session_id}")
    try:
        while True:
            data = await websocket.receive_bytes()
            
            await websocket.send_json({
                "type": "audio_received",
                "size": len(data)
            })
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, f"voice_{session_id}")

