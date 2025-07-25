from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import asyncio
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from firmware_builder.builder import FirmwareBuilder

# Initialize firmware builder
FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), '../../firmware')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../firmware')
firmware_builder = FirmwareBuilder(FIRMWARE_DIR, OUTPUT_DIR)

class BuildRequest(BaseModel):
    version: Optional[str] = None
    force: bool = False

@app.post("/firmware/build")
async def build_firmware(request: BuildRequest, background_tasks: BackgroundTasks):
    """Build new firmware version"""
    try:
        def build():
            result = firmware_builder.build_firmware()
            if result:
                return {"status": "success", "firmware": result}
            return {"status": "error", "message": "Build failed"}
        
        # Run build in background
        background_tasks.add_task(build)
        return {"status": "building"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/firmware/latest")
async def get_latest_firmware():
    """Get latest firmware info"""
    latest = firmware_builder.get_latest_firmware()
    if not latest:
        return {"status": "no_firmware"}
    return latest

@app.get("/firmware/download/{version}")
async def download_firmware(version: str):
    """Download specific firmware version"""
    firmware_path = firmware_builder.get_firmware_path(version)
    if not firmware_path:
        raise HTTPException(status_code=404, detail="Firmware version not found")
    return FileResponse(firmware_path)
