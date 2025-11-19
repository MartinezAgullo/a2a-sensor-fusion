"""
Prototype 4: Visual Sensor Agent
=================================
Full A2A SDK integration using:
- AgentExecutor for business logic
- EventQueue for streaming responses
- A2AStarletteApplication for server

Port: 8002
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

from models import VisualData, SensorTaskParams
import json


# ============================================================================
# VISUAL SENSOR BUSINESS LOGIC
# ============================================================================

class VisualSensor:
    """
    Core visual sensor logic.
    Simulates computer vision / ML classification.
    """
    
    def __init__(self):
        self.sensor_id = "VISUAL-001"
        self.status = "operational"
    
    async def classify_target(self, sector_id: str) -> VisualData:
        """
        Perform visual classification of target.
        
        In production, this would use actual computer vision models.
        For prototype, we simulate classification results.
        """
        # Simulate visual classification
        classifications = ["drone", "aircraft", "vessel", "unknown"]
        classification = random.choice(classifications)
        certainty = random.randint(60, 99)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        return VisualData(
            classification=classification,
            certainty_percent=certainty,
            timestamp=timestamp
        )


# ============================================================================
# A2A AGENT EXECUTOR
# ============================================================================

class VisualAgentExecutor(AgentExecutor):
    """
    A2A AgentExecutor implementation for Visual Sensor.
    
    Handles:
    - Task execution via execute()
    - Event streaming via EventQueue
    - Graceful cancellation via cancel()
    """
    
    def __init__(self):
        self.sensor = VisualSensor()
        print(f"[Visual Agent] Initialized - Sensor ID: {self.sensor.sensor_id}")
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute visual classification task.
        
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
            
            print(f"\n[Visual Agent] 👁️  Executing task for sector: {sector_id}")
            
            # Optional: Send progress update (streaming capability)
            await event_queue.enqueue_event(
                new_agent_text_message("🔄 Analyzing visual data...")
            )
            
            # Perform visual classification
            visual_data = await self.sensor.classify_target(sector_id)
            
            print(f"[Visual Agent] ✓ Classification: {visual_data.classification.upper()} ({visual_data.certainty_percent}%)")
            
            # Send result as JSON
            result_json = visual_data.model_dump_json()
            await event_queue.enqueue_event(
                new_agent_text_message(result_json)
            )
            
        except Exception as e:
            print(f"[Visual Agent] ✗ Error during execution: {e}")
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
        
        In production, this would abort ML inference.
        """
        print(f"[Visual Agent] ⚠️  Task cancellation requested")
        await event_queue.enqueue_event(
            new_agent_text_message("Task cancelled by request")
        )


# ============================================================================
# AGENT CARD DEFINITION
# ============================================================================

VISUAL_AGENT_CARD = AgentCard(
    name="Visual Sensor Agent",
    description="Provides visual target classification using computer vision with confidence scoring",
    url="http://localhost:8002",
    version="2.0.0",  # Prototype 4
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(
        streaming=True,  # Now supports streaming!
        cancellable=True,  # Now supports cancellation!
    ),
    skills=[
        AgentSkill(
            id="visual_classification",
            name="Visual Target Classification",
            description="Classifies targets using visual sensors and computer vision algorithms",
            tags=["visual", "sensor", "classification", "computer-vision"],
            examples=[
                "Classify target in Alpha Sector",
                "Identify aerial contact type",
                "Determine target classification"
            ]
        )
    ],
)


# ============================================================================
# A2A SERVER SETUP
# ============================================================================

# Create request handler with executor and task store
request_handler = DefaultRequestHandler(
    agent_executor=VisualAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

# Create A2A Starlette application
server = A2AStarletteApplication(
    agent_card=VISUAL_AGENT_CARD,
    http_handler=request_handler,
)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 PROTOTYPE 4: VISUAL AGENT (Full A2A SDK)")
    print("="*70)
    print(f"Agent: {VISUAL_AGENT_CARD.name}")
    print(f"Version: {VISUAL_AGENT_CARD.version}")
    print(f"Port: 8002")
    print(f"Streaming: {VISUAL_AGENT_CARD.capabilities.streaming}")
    #print(f"Cancellable: {VISUAL_AGENT_CARD.capabilities.cancellable}")
    print("="*70 + "\n")
    
    uvicorn.run(
        server.build(), 
        host="0.0.0.0", 
        port=8002,
        log_level="info"
    )