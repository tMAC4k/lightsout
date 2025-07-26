#!/bin/bash

# LightsOut Deployment Script
echo "🚀 LightsOut Deployment Script"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script must be run on a Raspberry Pi!"
    exit 1
fi

# Install minimal system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git

# Setup paths
VENV_PATH="$HOME/lightsout_env"
REPO_PATH="$HOME/lightsout"

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

# Clone repository
echo "📥 Setting up repository..."
rm -rf "$REPO_PATH"
git clone https://github.com/tMAC4k/lightsout.git "$REPO_PATH"

# Install Python requirements
echo "📦 Installing Python packages..."
cd "$REPO_PATH/server"
pip install --upgrade pip
pip install -r requirements.txt

# Create basic service
echo "🔧 Creating service..."
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

sudo systemctl daemon-reload
sudo systemctl enable lightsout
sudo systemctl start lightsout

echo "✅ Installation complete!"
echo "💡 Service status: sudo systemctl status lightsout"
