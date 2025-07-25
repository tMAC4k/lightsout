import os
import subprocess
import shutil
import json
from datetime import datetime
from typing import Optional
import platformio.project.config

class FirmwareBuilder:
    def __init__(self, firmware_dir: str, output_dir: str):
        self.firmware_dir = firmware_dir
        self.output_dir = output_dir
        self.version_file = os.path.join(firmware_dir, "version.json")
        self._load_version()
    
    def _load_version(self):
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                self.version_info = json.load(f)
        else:
            self.version_info = {
                "version": "1.0.0",
                "builds": []
            }
    
    def _save_version(self):
        with open(self.version_file, 'w') as f:
            json.dump(self.version_info, f, indent=2)
    
    def _increment_version(self):
        major, minor, patch = map(int, self.version_info["version"].split("."))
        patch += 1
        self.version_info["version"] = f"{major}.{minor}.{patch}"
    
    def build_firmware(self) -> Optional[str]:
        try:
            # Update version
            self._increment_version()
            version = self.version_info["version"]
            
            # Update build flags in platformio.ini
            config = platformio.project.config.ProjectConfig(
                os.path.join(self.firmware_dir, "platformio.ini")
            )
            config.update("build_flags", f"-D VERSION='\"{version}\"'")
            
            # Build firmware
            result = subprocess.run(
                ["platformio", "run"],
                cwd=self.firmware_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Build failed: {result.stderr}")
                return None
            
            # Copy firmware to output directory
            build_dir = os.path.join(self.firmware_dir, ".pio", "build", "heltec_wifi_lora_32_V3")
            firmware_file = os.path.join(build_dir, "firmware.bin")
            
            if not os.path.exists(firmware_file):
                print("Firmware file not found")
                return None
            
            # Create output filename with version
            output_name = f"firmware_v{version}.bin"
            output_path = os.path.join(self.output_dir, output_name)
            
            # Copy firmware file
            shutil.copy2(firmware_file, output_path)
            
            # Update version info
            self.version_info["builds"].append({
                "version": version,
                "filename": output_name,
                "date": datetime.now().isoformat(),
                "size": os.path.getsize(output_path)
            })
            self._save_version()
            
            return output_name
            
        except Exception as e:
            print(f"Build failed: {e}")
            return None
    
    def get_latest_firmware(self) -> Optional[dict]:
        if not self.version_info["builds"]:
            return None
        return self.version_info["builds"][-1]
    
    def get_firmware_path(self, version: str) -> Optional[str]:
        for build in self.version_info["builds"]:
            if build["version"] == version:
                return os.path.join(self.output_dir, build["filename"])
        return None
