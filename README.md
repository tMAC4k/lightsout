# LightsOut - RF Mesh Light Control System

A secure IoT light control system using LoRa mesh networking with OTA updates, RTL-SDR monitoring, and web dashboard.

## Features

### 🎯 Core Features
- LoRa mesh networking for reliable communication
- WiFi-based OTA updates
- LwM2M device management
- RTL-SDR RF monitoring
- Real-time web dashboard
- Interactive OLED menu system

### 🔐 Security
- Encrypted LoRa communications
- Signed OTA updates
- TLS for server communications
- RF spectrum monitoring

## Quick Start

### 🚀 One-Command Installation
On your Raspberry Pi, run:
```bash
wget -O- https://raw.githubusercontent.com/tMAC4k/lightsout/main/tools/deploy_system.sh | bash
```

This will:
- Install all dependencies
- Set up the server and agent
- Configure RTL-SDR
- Create system service
- Set up web dashboard

### 📱 Web Dashboard
Access at: `http://your-raspberry-pi:5000/dashboard`
- Real-time node status
- Interactive map
- Signal strength monitoring
- Message history

### 🛠️ Command Line Interface
```bash
# Monitor RF activity
lightsout monitor

# View connected devices
lightsout devices

# Check system status
lightsout status
```

## Components

### 1. Firmware (Heltec WiFi LoRa 32 V3)
- FreeRTOS multitasking
- Interactive OLED menu
- WiFi + LoRa communication
- LwM2M client support
- OTA update capability

### 2. Server/Agent
- FastAPI backend
- RTL-SDR integration
- LwM2M server
- Real-time WebSocket updates
- Docker containerization

### 3. Tools
- RF spectrum analyzer
- Packet sniffer
- Signal strength mapper
- Firmware builder

## Development

### Building Firmware
```bash
cd firmware
platformio run -t upload
```

### Server Development
```bash
cd server
docker-compose up --build
```

### Required VS Code Extensions
- PlatformIO IDE
- Python
- Docker

## Documentation

### 📡 RF Specifications
- LoRa Frequency: 868 MHz
- RTL-SDR Monitoring: 850-900 MHz
- Signal Strength Tracking

### 🌐 Network
- LwM2M Port: 5683
- Web Dashboard: 5000
- WebSocket: 5000/ws

### 📊 Telemetry Data
- Signal strength (RSSI)
- Node locations
- Message statistics
- System health

## Troubleshooting

### Common Issues
1. RTL-SDR Access
```bash
sudo usermod -a -G plugdev $USER
```

2. LoRa Connection
```bash
lightsout scan
```

3. Service Status
```bash
systemctl status lightsout
```

## License
MIT License
