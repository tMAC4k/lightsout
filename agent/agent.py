#!/usr/bin/env python3

import serial
import time
import requests
import asyncio
import aiocoap
import json
from typing import Optional

class LoRaAgent:
    def __init__(self, port: str = "/dev/ttyUSB0", baud: int = 115200):
        self.port = port
        self.baud = baud
        self.serial: Optional[serial.Serial] = None
        self.coap_client: Optional[aiocoap.Context] = None
    
    def connect_serial(self):
        try:
            self.serial = serial.Serial(self.port, self.baud)
            print(f"Connected to {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    async def setup_coap(self):
        self.coap_client = await aiocoap.Context.create_client_context()
    
    async def send_telemetry(self, data: dict):
        if not self.coap_client:
            await self.setup_coap()
        
        payload = json.dumps(data).encode()
        request = aiocoap.Message(
            code=aiocoap.POST,
            payload=payload,
            uri='coap://localhost/telemetry'
        )
        
        try:
            response = await self.coap_client.request(request).response
            print(f"Telemetry sent. Response: {response.code}")
        except Exception as e:
            print(f"Failed to send telemetry: {e}")
    
    def send_lora_packet(self, data: bytes):
        if self.serial and self.serial.is_open:
            self.serial.write(data)
            return True
        return False
    
    def receive_lora_packet(self) -> Optional[bytes]:
        if self.serial and self.serial.is_open:
            if self.serial.in_waiting:
                return self.serial.readline()
        return None
    
    async def check_updates(self):
        try:
            response = requests.get('http://localhost:5000/firmware/latest')
            if response.status_code == 200:
                firmware_info = response.json()
                if firmware_info.get('update_available'):
                    print("New firmware available!")
                    # Download and send to node
                    self.send_lora_packet(b'UPDATE_AVAILABLE')
        except Exception as e:
            print(f"Failed to check updates: {e}")
    
    async def run(self):
        if not self.connect_serial():
            return
        
        await self.setup_coap()
        
        while True:
            # Check for incoming LoRa messages
            packet = self.receive_lora_packet()
            if packet:
                await self.send_telemetry({'type': 'lora_rx', 'data': packet.hex()})
            
            # Check for updates periodically
            await self.check_updates()
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    agent = LoRaAgent()
    asyncio.run(agent.run())
