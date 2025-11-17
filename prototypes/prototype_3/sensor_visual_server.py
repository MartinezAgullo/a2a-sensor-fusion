"""
Visual Sensor Agent (A2A Server)
=================================
Remote agent that provides simulated visual classification data.
Runs on Port 8002.

Phase 2: Added AgentCard endpoint for A2A discovery
"""

from fastapi import FastAPI
from models import A2ATask, VisualData, AgentCard, AgentSkill, AgentCapabilities
import random

app = FastAPI(title="Visual Sensor Agent", version="1.0.0")

# ============================================================================
# AGENT CARD DEFINITION (A2A Discovery)
# ============================================================================

VISUAL_AGENT_CARD = AgentCard(
    name="Visual Sensor Agent",
    description="Provides visual target classification using computer vision with confidence scoring. Identifies target types (drone, aircraft, vessel, unknown) with certainty assessment.",
    url="http://localhost:8002",
    version="1.0.0",
    skills=[
        AgentSkill(
            id="visual_classification",
            name="Visual Target Classification",
            description="Classifies targets using visual sensors and computer vision algorithms. Returns target type and classification certainty percentage.",
            input_format="A2ATask (sector_id, request_type)",
            output_format="VisualData (classification, certainty_percent)",
            tags=["visual", "sensor", "classification", "computer-vision", "image-processing"],
            examples=[
                "Classify target in Alpha Sector",
                "Identify aerial contact type",
                "Determine target classification visually",
                "Assess vessel type with confidence"
            ]
        )
    ],
    capabilities=AgentCapabilities(
        streaming=False,
        batch_processing=False,
        cancellable=False,
        max_concurrent_tasks=5,
        average_response_time_ms=150
    ),
    default_input_modes=["application/json"],
    default_output_modes=["application/json"],
    author="Defense Systems Lab",
    tags=["sensor", "visual", "defense", "classification", "computer-vision"]
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
    return VISUAL_AGENT_CARD


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "agent": "Visual Sensor Agent",
        "status": "operational",
        "capability": "Target classification and certainty assessment",
        "version": VISUAL_AGENT_CARD.version,
        "discovery": "GET /card for full agent capabilities"
    }


@app.post("/process_task", response_model=VisualData)
async def process_task(task: A2ATask) -> VisualData:
    """
    A2A Server Endpoint: Processes incoming task and returns visual classification data.
    
    Args:
        task: A2A task request from Fusion Agent
        
    Returns:
        VisualData: Simulated visual classification with certainty
    """
    print(f"\n[Visual Agent | A2A Server] 👁️  Received Task ID {task.task_id[:8]}...")
    print(f"[Visual Agent] Sector: {task.sector_id}")
    
    # Simulate visual classification
    # In a real system, this would use computer vision/ML models
    classifications = ["drone", "aircraft", "vessel", "unknown"]
    simulated_class = random.choice(classifications)
    simulated_certainty = random.randint(60, 99)  # 60-99% confidence
    
    visual_reading = VisualData(
        classification=simulated_class,
        certainty_percent=simulated_certainty
    )
    
    print(f"[Visual Agent] ✓ Classification: {visual_reading.classification.upper()} ({visual_reading.certainty_percent}% certain)")
    
    return visual_reading


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Visual Agent on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)