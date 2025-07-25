#!/bin/bash

# LightsOut Deployment Script
echo "🚀 LightsOut Deployment Script"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script must be run on a Raspberry Pi!"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    rtl-sdr \
    librtlsdr-dev \
    docker.io \
    docker-compose

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv ~/lightsout_env
source ~/lightsout_env/bin/activate

# Clone repository if not exists
if [ ! -d "~/lightsout" ]; then
    echo "📥 Cloning LightsOut repository..."
    git clone https://github.com/tMAC4k/lightsout.git ~/lightsout
fi

# Install Python requirements
cd ~/lightsout/server
pip install -r requirements.txt

# Create service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/lightsout.service << EOF
[Unit]
Description=LightsOut Control System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/lightsout/server
Environment="PATH=/home/$USER/lightsout_env/bin:$PATH"
ExecStart=/home/$USER/lightsout_env/bin/python src/cli/control_center.py server
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable lightsout
sudo systemctl start lightsout

echo "✅ Installation complete!"
echo "💡 Usage:"
echo "  - Control center: lightsout"
echo "  - Monitor RF: lightsout monitor"
echo "  - View devices: lightsout devices"
echo ""
echo "🔄 The service will start automatically on boot"
echo "📝 Check logs with: journalctl -u lightsout -f"
