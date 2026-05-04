from fastapi import WebSocket
from typing import Dict, List
import json
from uuid import UUID

class ConnectionManager:
    def __init__(self):
        # room_id (negotiation_id) -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            disconnected_clients = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected_clients.append(connection)
            
            for client in disconnected_clients:
                self.disconnect(client, room_id)

manager = ConnectionManager()
