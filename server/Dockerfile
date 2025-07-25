FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    librtlsdr-dev \
    rtl-sdr \
    libusb-1.0-0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create firmware directory
RUN mkdir -p /firmware

# Make the CLI executable
RUN chmod +x src/cli/control_center.py

# Create symlink for easy access
RUN ln -s /app/src/cli/control_center.py /usr/local/bin/lightsout

# Default to CLI if no arguments provided
ENTRYPOINT ["lightsout"]
CMD ["server"]
