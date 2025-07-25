#!/bin/bash

# LightsOut Firmware Deployment Script
echo "📡 LightsOut Firmware Deployment"

# Check if PlatformIO is installed
if ! command -v platformio &> /dev/null; then
    echo "❌ PlatformIO not found. Installing..."
    python3 -m pip install --user platformio
fi

# Build firmware
echo "🔧 Building firmware..."
cd firmware
platformio run

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📤 Firmware is ready at: .pio/build/heltec_wifi_lora_32_V3/firmware.bin"
    
    # Optional: Upload directly if device is connected
    read -p "Upload to device? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Uploading firmware..."
        platformio run --target upload
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
