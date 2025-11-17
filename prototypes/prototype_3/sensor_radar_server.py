"""
Radar Sensor Agent (A2A Server)
================================
Remote agent that provides simulated radar data in polar coordinates.
Runs on Port 8001.

Phase 2: Added AgentCard endpoint for A2A discovery
"""

from fastapi import FastAPI
from models import A2ATask, RadarData, AgentCard, AgentSkill, AgentCapabilities
import random

app = FastAPI(title="Radar Sensor Agent", version="1.0.0")

# ============================================================================
# AGENT CARD DEFINITION (A2A Discovery)
# ============================================================================

RADAR_AGENT_CARD = AgentCard(
    name="Radar Sensor Agent",
    description="Provides radar-based target tracking with range and azimuth data in polar coordinates. Uses simulated radar hardware for target detection and ranging.",
    url="http://localhost:8001",
    version="1.0.0",
    skills=[
        AgentSkill(
            id="radar_detection",
            name="Radar Target Detection",
            description="Detects and tracks targets using radar, providing precise range (distance) and bearing (azimuth angle) in polar coordinate format",
            input_format="A2ATask (sector_id, request_type)",
            output_format="RadarData (range_meters, azimuth_degrees)",
            tags=["radar", "sensor", "tracking", "polar", "detection"],
            examples=[
                "Track target in Alpha Sector",
                "Scan sector for aerial contacts",
                "Provide range and bearing for Beta quadrant",
                "Detect targets in surveillance zone"
            ]
        )
    ],
    capabilities=AgentCapabilities(
        streaming=False,
        batch_processing=False,
        cancellable=False,
        max_concurrent_tasks=10,
        average_response_time_ms=50
    ),
    default_input_modes=["application/json"],
    default_output_modes=["application/json"],
    author="Defense Systems Lab",
    tags=["sensor", "radar", "defense", "tracking", "polar-coordinates"]
)


# ============================================================================
# AGENT CARD ENDPOINT (A2A Discovery)
# ============================================================================

@app.get("/card", response_model=AgentCard)
async def get_agent_card():
    """
    A2A Agent Card endpoint for dynamic discovery.
    
    Returns complete metadata about this agent's capabilities, skills,
    and technical characteristics. Used by client agents to discover
    and validate agent capabilities before sending tasks.
    """
    return RADAR_AGENT_CARD


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "agent": "Radar Sensor Agent",
        "status": "operational",
        "capability": "Range and bearing data (polar coordinates)",
        "version": RADAR_AGENT_CARD.version,
        "discovery": "GET /card for full agent capabilities"
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