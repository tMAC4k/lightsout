#!/bin/bash

# LightsOut Deployment Script
# This script will set up the complete LightsOut system on a Raspberry Pi

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 LightsOut System Deployment${NC}"
echo "----------------------------------------"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo -e "${RED}❌ This script must be run on a Raspberry Pi!${NC}"
    exit 1
fi

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 successful${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Install system dependencies
echo -e "\n${YELLOW}📦 Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    rtl-sdr \
    librtlsdr-dev \
    docker.io \
    docker-compose \
    build-essential \
    libusb-1.0-0-dev \
    pkg-config

check_status "System dependencies installation"

# Setup Docker
echo -e "\n${YELLOW}🐳 Setting up Docker...${NC}"
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
check_status "Docker setup"

# Create Python virtual environment
echo -e "\n${YELLOW}🐍 Setting up Python environment...${NC}"
python3 -m venv ~/lightsout_env
source ~/lightsout_env/bin/activate
check_status "Python environment creation"

# Clone or update repository
if [ -d "~/lightsout" ]; then
    echo -e "\n${YELLOW}📥 Updating LightsOut repository...${NC}"
    cd ~/lightsout
    git pull origin main
else
    echo -e "\n${YELLOW}📥 Cloning LightsOut repository...${NC}"
    git clone https://github.com/tMAC4k/lightsout.git ~/lightsout
fi
check_status "Repository setup"

# Install Python requirements
echo -e "\n${YELLOW}📚 Installing Python packages...${NC}"
cd ~/lightsout/server
pip install -r requirements.txt
check_status "Python packages installation"

# Create configuration directory
echo -e "\n${YELLOW}⚙️ Setting up configuration...${NC}"
mkdir -p ~/.lightsout
cat > ~/.lightsout/config.json << EOF
{
    "server": {
        "host": "0.0.0.0",
        "port": 5000
    },
    "lwm2m": {
        "enabled": true,
        "port": 5683
    },
    "rtlsdr": {
        "enabled": true,
        "frequency": 868000000,
        "sample_rate": 2048000
    }
}
EOF
check_status "Configuration setup"

# Setup systemd service
echo -e "\n${YELLOW}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/lightsout.service << EOF
[Unit]
Description=LightsOut Control System
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/lightsout/server
Environment="PATH=/home/$USER/lightsout_env/bin:$PATH"
ExecStart=/home/$USER/lightsout_env/bin/python src/cli/control_center.py server
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable lightsout
sudo systemctl start lightsout
check_status "Service setup"

# Set up udev rules for RTL-SDR
echo -e "\n${YELLOW}📻 Setting up RTL-SDR access...${NC}"
sudo tee /etc/udev/rules.d/20-rtlsdr.rules << EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="plugdev", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
check_status "RTL-SDR setup"

echo -e "\n${GREEN}✅ Installation complete!${NC}"
echo -e "\n${YELLOW}💡 Usage:${NC}"
echo "  - Control center: lightsout"
echo "  - Monitor RF: lightsout monitor"
echo "  - View devices: lightsout devices"
echo "  - Web dashboard: http://$(hostname -I | cut -d' ' -f1):5000/dashboard"
echo -e "\n${YELLOW}📝 Logs:${NC}"
echo "  - View logs: journalctl -u lightsout -f"
echo -e "\n${YELLOW}🔄 Services:${NC}"
echo "  - Restart service: sudo systemctl restart lightsout"
echo "  - Check status: sudo systemctl status lightsout"

# Check if reboot is needed
if [ -f /var/run/reboot-required ]; then
    echo -e "\n${RED}⚠️ A system reboot is required to complete the setup${NC}"
    read -p "Would you like to reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
fi
