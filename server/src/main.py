from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import serial
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI()

# Configuration
FIRMWARE_DIR = '/firmware'
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

class TelemetryData(BaseModel):
    node_id: str
    timestamp: str
    data: Dict[str, Any]

class LoRaHandler:
    def __init__(self, port: str = SERIAL_PORT, baud: int = BAUD_RATE):
        self.port = port
        self.baud = baud
        self.serial: Optional[serial.Serial] = None
        
    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(self.port, self.baud)
            print(f"Connected to {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def send_packet(self, data: bytes) -> bool:
        if self.serial and self.serial.is_open:
            self.serial.write(data)
            return True
        return False
    
    def receive_packet(self) -> Optional[bytes]:
        if self.serial and self.serial.is_open:
            if self.serial.in_waiting:
                return self.serial.readline()
        return None

# Global LoRa handler instance
lora_handler = LoRaHandler()

@app.on_event("startup")
async def startup_event():
    # Initialize LoRa connection
    if not lora_handler.connect():
        print("Warning: Failed to initialize LoRa connection")
    
    # Start background tasks
    asyncio.create_task(process_lora_messages())

async def process_lora_messages():
    while True:
        if lora_handler.serial:
            packet = lora_handler.receive_packet()
            if packet:
                try:
                    # Process received packet
                    data = json.loads(packet.decode())
                    # Store telemetry, trigger actions, etc.
                    print(f"Received LoRa packet: {data}")
                except json.JSONDecodeError:
                    print(f"Invalid packet format: {packet}")
        await asyncio.sleep(0.1)

@app.get("/firmware/latest")
async def get_latest_firmware():
    try:
        files = [f for f in os.listdir(FIRMWARE_DIR) if f.endswith('.bin')]
        if not files:
            return {"update_available": False}
        
        latest = max(files, key=lambda f: os.path.getctime(os.path.join(FIRMWARE_DIR, f)))
        
        return {
            "update_available": True,
            "version": latest.split('.')[0],
            "filename": latest,
            "size": os.path.getsize(os.path.join(FIRMWARE_DIR, latest)),
            "date": datetime.fromtimestamp(
                os.path.getctime(os.path.join(FIRMWARE_DIR, latest))
            ).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/firmware/download/{filename}")
async def download_firmware(filename: str):
    file_path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Firmware file not found")
    return FileResponse(file_path)

@app.post("/node/{node_id}/command")
async def send_command(node_id: str, command: str):
    packet = json.dumps({
        "type": "command",
        "node": node_id,
        "command": command
    }).encode()
    
    if lora_handler.send_packet(packet):
        return {"status": "sent"}
    raise HTTPException(status_code=500, detail="Failed to send command")

@app.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    # Process and store telemetry data
    print(f"Received telemetry from node {data.node_id}: {data.data}")
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
