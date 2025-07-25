# LightsOut - RF Mesh Light Control System

A secure IoT light control system using LoRa mesh networking with OTA update capabilities.

## Components

### 1. Firmware (ESP32 - Heltec WiFi LoRa 32 V3)
- LoRa mesh networking
- Light control simulation
- OTA update support
- FreeRTOS task management

### 2. Agent (Raspberry Pi)
- LoRa to Server bridge
- CoAP/LwM2M client
- OTA update distribution
- Telemetry collection

### 3. Server
- Eclipse Leshan LwM2M server
- Flask API for firmware management
- Docker containerization
- OTA update repository

### 4. Tools
- RF packet sniffer
- Packet replay utility (TODO)

## Setup Instructions

### Firmware
1. Install PlatformIO Core
2. Navigate to firmware directory
3. Build and flash:
   ```bash
   platformio run -t upload
   ```

### Agent
1. Install requirements:
   ```bash
   pip install pyserial requests aiocoap
   ```
2. Run the agent:
   ```bash
   python agent/agent.py
   ```

### Server
1. Build and start containers:
   ```bash
   cd server
   docker-compose up -d
   ```

### Tools
1. Run RF sniffer:
   ```bash
   python tools/rf_sniffer.py -p /dev/ttyUSB0
   ```

## Development

### Required VS Code Extensions
- PlatformIO IDE
- Python
- Docker

## Security Notes
- Implement proper encryption for LoRa communications
- Secure OTA updates with signatures
- Use TLS for server communications
- Monitor RF spectrum for interference

## License
MIT
