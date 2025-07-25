from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import json
import asyncio
from typing import Dict, List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Node:
    def __init__(self, id: str, lat: float = 0, lng: float = 0):
        self.id = id
        self.lat = lat
        self.lng = lng
        self.status = "offline"
        self.rssi = 0
        self.last_seen = datetime.now()
        self.messages = []

    def update(self, data: dict):
        self.rssi = data.get('rssi', self.rssi)
        self.status = "online"
        self.last_seen = datetime.now()
        if 'lat' in data and 'lng' in data:
            self.lat = data['lat']
            self.lng = data['lng']
        self.messages.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        # Keep only last 100 messages
        self.messages = self.messages[-100:]

    def to_dict(self):
        return {
            'id': self.id,
            'lat': self.lat,
            'lng': self.lng,
            'status': self.status,
            'rssi': self.rssi,
            'lastSeen': self.last_seen.isoformat()
        }

class DashboardManager:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.connections: Set[WebSocket] = set()
        self.message_count = 0
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        await self.broadcast_state()
    
    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
    
    def update_node(self, node_id: str, data: dict):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id)
        self.nodes[node_id].update(data)
        self.message_count += 1
    
    def get_stats(self):
        active_nodes = sum(1 for node in self.nodes.values() if node.status == "online")
        avg_rssi = sum(node.rssi for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        
        return {
            'activeNodes': active_nodes,
            'totalMessages': self.message_count,
            'avgRssi': round(avg_rssi, 2)
        }
    
    async def broadcast_state(self):
        if not self.connections:
            return
        
        message = {
            'stats': self.get_stats(),
            'nodes': [node.to_dict() for node in self.nodes.values()]
        }
        
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")

# Create dashboard manager instance
dashboard = DashboardManager()

# FastAPI routes
app.mount("/dashboard", StaticFiles(directory="src/dashboard", html=True), name="dashboard")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await dashboard.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard.disconnect(websocket)

@app.post("/telemetry/{node_id}")
async def receive_telemetry(node_id: str, data: dict):
    dashboard.update_node(node_id, data)
    asyncio.create_task(dashboard.broadcast_state())
    return {"status": "received"}
