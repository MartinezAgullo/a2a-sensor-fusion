"""
Radar Sensor Agent (A2A Server)
================================
Remote agent that provides simulated radar data in polar coordinates.
Runs on Port 8001.
"""

from fastapi import FastAPI
from models import A2ATask, RadarData
import random

app = FastAPI(title="Radar Sensor Agent", version="1.0.0")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "agent": "Radar Sensor Agent",
        "status": "operational",
        "capability": "Range and bearing data (polar coordinates)"
    }


@app.post("/process_task", response_model=RadarData)
async def process_task(task: A2ATask) -> RadarData:
    """
    A2A Server Endpoint: Processes incoming task and returns radar data.
    
    Args:
        task: A2A task request from Fusion Agent
        
    Returns:
        RadarData: Simulated radar sensor reading in polar coordinates
    """
    print(f"\n[Radar Agent | A2A Server] 📡 Received Task ID {task.task_id[:8]}...")
    print(f"[Radar Agent] Sector: {task.sector_id}")
    
    # Simulate radar sensor reading
    # In a real system, this would interface with actual radar hardware/software
    simulated_range = random.uniform(500, 3000)  # 0.5-3 km range
    simulated_azimuth = random.uniform(0, 360)    # 0-360 degrees
    
    radar_reading = RadarData(
        range_meters=round(simulated_range, 1),
        azimuth_degrees=round(simulated_azimuth, 1)
    )
    
    print(f"[Radar Agent] ✓ Generated reading: {radar_reading.range_meters}m @ {radar_reading.azimuth_degrees}°")
    
    return radar_reading


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Radar Agent on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)