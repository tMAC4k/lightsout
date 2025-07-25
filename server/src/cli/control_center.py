#!/usr/bin/env python3

import click
import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text
from rich.table import Table
import rtlsdr

console = Console()

LOGO = """
╔══════════════════════════════════════╗
║     LightsOut Control Center v1.0     ║
║        RF Mesh Control System         ║
╚══════════════════════════════════════╝
"""

def show_splash():
    console.print(Panel(LOGO, style="bold blue"))
    with Progress() as progress:
        task = progress.add_task("[cyan]Initializing...", total=100)
        while not progress.finished:
            progress.update(task, advance=0.7)
            time.sleep(0.02)

class ModuleLogger:
    def __init__(self, module_name):
        self.module_name = module_name
    
    def log(self, msg_type, message):
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}][{self.module_name}][{msg_type}] {message}"
        if msg_type == "ERROR":
            console.print(formatted, style="red")
        elif msg_type == "WARNING":
            console.print(formatted, style="yellow")
        else:
            console.print(formatted, style="green")

class RTLSDRScanner:
    def __init__(self):
        self.logger = ModuleLogger("RTL-SDR")
        self.sdr = None
    
    def init_device(self):
        try:
            self.sdr = rtlsdr.RtlSdr()
            self.sdr.sample_rate = 2.048e6
            self.sdr.center_freq = 868e6  # LoRa frequency
            self.sdr.gain = 'auto'
            self.logger.log("INFO", "RTL-SDR initialized successfully")
            return True
        except Exception as e:
            self.logger.log("ERROR", f"Failed to initialize RTL-SDR: {e}")
            return False
    
    def scan(self, duration=10):
        if not self.sdr:
            self.logger.log("ERROR", "RTL-SDR not initialized")
            return
        
        self.logger.log("INFO", f"Starting {duration}s RF scan...")
        try:
            samples = self.sdr.read_samples(256*1024)
            # Process samples (implement RF analysis here)
            self.logger.log("INFO", f"Captured {len(samples)} samples")
        except Exception as e:
            self.logger.log("ERROR", f"Scan failed: {e}")

@click.group()
def cli():
    """LightsOut Control Center - RF Mesh Control System"""
    pass

@cli.command()
def monitor():
    """Monitor RF activity using RTL-SDR"""
    scanner = RTLSDRScanner()
    if scanner.init_device():
        while True:
            try:
                scanner.scan()
                time.sleep(1)
            except KeyboardInterrupt:
                break

@cli.command()
@click.option('--host', default='localhost', help='Server hostname')
@click.option('--port', default=5000, help='Server port')
def server(host, port):
    """Start the LwM2M server and RF bridge"""
    logger = ModuleLogger("LwM2M")
    logger.log("INFO", f"Starting server on {host}:{port}")
    # Import and start FastAPI server here
    from ..main import app
    import uvicorn
    uvicorn.run(app, host=host, port=port)

@cli.command()
def devices():
    """List connected devices and their status"""
    logger = ModuleLogger("DeviceManager")
    table = Table(title="Connected Devices")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Last Seen", style="yellow")
    
    # Add sample data (replace with actual device tracking)
    table.add_row("node_001", "Light Controller", "Online", "2m ago")
    table.add_row("node_002", "Light Controller", "Offline", "1h ago")
    
    console.print(table)

if __name__ == '__main__':
    show_splash()
    cli()
