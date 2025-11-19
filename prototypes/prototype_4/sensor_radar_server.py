"""
Prototype 4: Radar Sensor Agent
================================
Full A2A SDK integration using:
- AgentExecutor for business logic
- EventQueue for streaming responses
- A2AStarletteApplication for server

Port: 8001
"""

import random
from datetime import datetime
from typing import Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)
from a2a.utils import new_agent_text_message

from models import RadarData, SensorTaskParams
import json


# ============================================================================
# RADAR SENSOR BUSINESS LOGIC
# ============================================================================

class RadarSensor:
    """
    Core radar sensor logic.
    Simulates hardware interface for target detection.
    """
    
    def __init__(self):
        self.sensor_id = "RADAR-001"
        self.status = "operational"
    
    async def scan_sector(self, sector_id: str) -> RadarData:
        """
        Perform radar scan of specified sector.
        
        In production, this would interface with actual radar hardware.
        For prototype, we simulate realistic measurements.
        """
        # Simulate radar detection
        range_meters = round(random.uniform(500, 3000), 1)
        azimuth_degrees = round(random.uniform(0, 360), 1)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        return RadarData(
            range_meters=range_meters,
            azimuth_degrees=azimuth_degrees,
            timestamp=timestamp
        )


# ============================================================================
# A2A AGENT EXECUTOR
# ============================================================================

class RadarAgentExecutor(AgentExecutor):
    """
    A2A AgentExecutor implementation for Radar Sensor.
    
    Handles:
    - Task execution via execute()
    - Event streaming via EventQueue
    - Graceful cancellation via cancel()
    """
    
    def __init__(self):
        self.sensor = RadarSensor()
        print(f"[Radar Agent] Initialized - Sensor ID: {self.sensor.sensor_id}")
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute radar detection task.
        
        Args:
            context: Request context with task parameters
            event_queue: Queue for sending response events
        """
        try:
            # Extract parameters from request
            params_dict = context.request.params.get("message", {}).get("parts", [{}])[0]
            text_content = params_dict.get("text", "")
            
            # Parse task parameters
            try:
                task_params = SensorTaskParams.model_validate_json(text_content)
                sector_id = task_params.sector_id
            except Exception:
                # Fallback: try to extract sector from text
                sector_id = "Alpha Sector"  # Default
            
            print(f"\n[Radar Agent] 📡 Executing task for sector: {sector_id}")
            
            # Optional: Send progress update (streaming capability)
            await event_queue.enqueue_event(
                new_agent_text_message("🔄 Initiating radar scan...")
            )
            
            # Perform radar scan
            radar_data = await self.sensor.scan_sector(sector_id)
            
            print(f"[Radar Agent] ✓ Scan complete: {radar_data.range_meters}m @ {radar_data.azimuth_degrees}°")
            
            # Send result as JSON
            result_json = radar_data.model_dump_json()
            await event_queue.enqueue_event(
                new_agent_text_message(result_json)
            )
            
        except Exception as e:
            print(f"[Radar Agent] ✗ Error during execution: {e}")
            error_msg = json.dumps({"error": str(e)})
            await event_queue.enqueue_event(
                new_agent_text_message(error_msg)
            )
    
    async def cancel(
        self, 
        context: RequestContext, 
        event_queue: EventQueue
    ) -> None:
        """
        Handle task cancellation.
        
        In production, this would abort hardware operations.
        """
        print(f"[Radar Agent] ⚠️  Task cancellation requested")
        await event_queue.enqueue_event(
            new_agent_text_message("Task cancelled by request")
        )


# ============================================================================
# AGENT CARD DEFINITION
# ============================================================================

RADAR_AGENT_CARD = AgentCard(
    name="Radar Sensor Agent",
    description="Provides radar-based target tracking with range and azimuth data in polar coordinates",
    url="http://localhost:8001",
    version="2.0.0",  # Prototype 4
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(
        streaming=True,  # Now supports streaming!
        cancellable=True,  # Now supports cancellation!
    ),
    skills=[
        AgentSkill(
            id="radar_detection",
            name="Radar Target Detection",
            description="Detects and tracks targets using radar, providing range and bearing in polar coordinates",
            tags=["radar", "sensor", "tracking", "polar"],
            examples=[
                "Scan Alpha Sector",
                "Track target in Beta quadrant",
                "Provide range and bearing data"
            ]
        )
    ],
)


# ============================================================================
# A2A SERVER SETUP
# ============================================================================

# Create request handler with executor and task store
request_handler = DefaultRequestHandler(
    agent_executor=RadarAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

# Create A2A Starlette application
server = A2AStarletteApplication(
    agent_card=RADAR_AGENT_CARD,
    http_handler=request_handler,
)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 PROTOTYPE 4: RADAR AGENT (Full A2A SDK)")
    print("="*70)
    print(f"Agent: {RADAR_AGENT_CARD.name}")
    print(f"Version: {RADAR_AGENT_CARD.version}")
    print(f"Port: 8001")
    print(f"Streaming: {RADAR_AGENT_CARD.capabilities.streaming}")
    #print(f"Cancellable: {RADAR_AGENT_CARD.capabilities.cancellable}")
    print("="*70 + "\n")
    
    uvicorn.run(
        server.build(), 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )