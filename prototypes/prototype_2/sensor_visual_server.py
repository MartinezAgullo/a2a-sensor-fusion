"""
Visual Sensor Agent (A2A Server)
=================================
Remote agent that provides simulated visual classification data.
Runs on Port 8002.
"""

from fastapi import FastAPI
from models import A2ATask, VisualData
import random

app = FastAPI(title="Visual Sensor Agent", version="1.0.0")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "agent": "Visual Sensor Agent",
        "status": "operational",
        "capability": "Target classification and certainty assessment"
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