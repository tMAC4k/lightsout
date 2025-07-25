#!/usr/bin/env python3

import serial
import argparse
import time
from datetime import datetime

class RFSniffer:
    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.serial = None
        self.log_file = f"rf_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baud)
            print(f"Connected to {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False
    
    def sniff(self, duration: int = 0):
        """Sniff RF packets for specified duration (0 = infinite)"""
        if not self.connect():
            return
        
        print(f"Starting RF sniffing, logging to {self.log_file}")
        start_time = time.time()
        
        try:
            with open(self.log_file, 'w') as log:
                while True:
                    if self.serial.in_waiting:
                        data = self.serial.readline()
                        timestamp = datetime.now().isoformat()
                        packet = data.hex()
                        log_line = f"[{timestamp}] {packet}\n"
                        print(log_line, end='')
                        log.write(log_line)
                        log.flush()
                    
                    if duration > 0 and (time.time() - start_time) >= duration:
                        break
        
        except KeyboardInterrupt:
            print("\nStopping RF sniffing...")
        finally:
            self.serial.close()

def main():
    parser = argparse.ArgumentParser(description="RF Packet Sniffer")
    parser.add_argument('-p', '--port', required=True, help='Serial port')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='Baud rate')
    parser.add_argument('-d', '--duration', type=int, default=0, 
                      help='Sniffing duration in seconds (0 = infinite)')
    
    args = parser.parse_args()
    
    sniffer = RFSniffer(args.port, args.baud)
    sniffer.sniff(args.duration)

if __name__ == "__main__":
    main()
