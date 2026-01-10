from typing import Dict, List, Set, Any
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.device_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, channel: str, device_id: str = None):
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
        if device_id:
            self.device_connections[device_id] = websocket
    
    def disconnect(self, websocket: WebSocket, channel: str, device_id: str = None):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        
        if device_id and device_id in self.device_connections:
            del self.device_connections[device_id]
    
    async def send_to_device(self, device_id: str, message: Dict[str, Any]):
        websocket = self.device_connections.get(device_id)
        if websocket:
            await websocket.send_json(message)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        connections = self.active_connections.get(channel, set())
        disconnected = []
        
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            connections.discard(ws)
    
    async def broadcast_order_update(self, order_data: Dict[str, Any]):
        await self.broadcast_to_channel("admin", {
            "type": "order_update",
            "data": order_data
        })
        
        device_id = order_data.get("device_id")
        if device_id:
            await self.send_to_device(device_id, {
                "type": "order_status",
                "data": order_data
            })


connection_manager = ConnectionManager()

