"""
Fusion Agent (A2A Client / Orchestrator)
=========================================
Main client agent that:
1. Sends A2A tasks to remote Sensor Agents
2. Collects disparate sensor data
3. Uses MCP tool to normalize data
4. Generates final A2A Artifact (fusion report)
"""

import httpx
import uuid
from models import A2ATask, RadarData, VisualData, A2AArtifact
from mcp_tool import data_normalization_tool


class FusionAgent:
    """
    Client Agent that orchestrates sensor fusion using A2A and MCP protocols.
    """
    
    def __init__(self, radar_url: str = "http://localhost:8001", 
                 visual_url: str = "http://localhost:8002"):
        self.radar_url = radar_url
        self.visual_url = visual_url
        
    async def execute_fusion(self, sector: str) -> A2AArtifact:
        """
        Execute the full sensor fusion workflow.
        
        Args:
            sector: Surveillance sector identifier
            
        Returns:
            A2AArtifact: Final fusion report with normalized target data
        """
        print("\n" + "="*70)
        print("🎯 FUSION AGENT ORCHESTRATION STARTING")
        print("="*70)
        
        # =====================================================================
        # A2A STEP 1: Create and send tasks to Sensor Agents
        # =====================================================================
        task = A2ATask(sector_id=sector)
        
        print(f"\n[Fusion Agent] 📤 Sending A2A Tasks to Sensor Agents...")
        print(f"[Fusion Agent] Task ID: {task.task_id}")
        print(f"[Fusion Agent] Target Sector: {sector}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Request data from Radar Agent
            print("\n[Fusion Agent] → Contacting Radar Agent (Port 8001)...")
            radar_response = await client.post(
                f"{self.radar_url}/process_task",
                json=task.model_dump()
            )
            radar_data = RadarData(**radar_response.json())
            
            # Request data from Visual Agent
            print("[Fusion Agent] → Contacting Visual Agent (Port 8002)...")
            visual_response = await client.post(
                f"{self.visual_url}/process_task",
                json=task.model_dump()
            )
            visual_data = VisualData(**visual_response.json())
        
        print("\n[Fusion Agent] ✅ Received raw data from both sensors")
        print(f"[Fusion Agent] Radar: {radar_data.range_meters}m @ {radar_data.azimuth_degrees}°")
        print(f"[Fusion Agent] Visual: {visual_data.classification.upper()} ({visual_data.certainty_percent}%)")
        
        # =====================================================================
        # MCP STEP: Normalize the disparate sensor data
        # =====================================================================
        print("\n[Fusion Agent] 🔄 Transitioning to MCP Tool Call...")
        normalized_target = data_normalization_tool(radar_data, visual_data)
        
        # =====================================================================
        # A2A STEP 2: Generate the final Artifact (Report)
        # =====================================================================
        fusion_id = f"RPT-{str(uuid.uuid4())[:8]}"
        report = A2AArtifact(
            fusion_id=fusion_id,
            targets=[normalized_target],
            summary=(
                f"Track successful for {sector}. "
                f"Detected 1 {normalized_target.target_type} target "
                f"at position ({normalized_target.x_pos}, {normalized_target.y_pos}) "
                f"with {normalized_target.confidence:.0%} confidence."
            )
        )
        
        print("\n[Fusion Agent] ✅ Successfully generated Final A2A Artifact")
        
        return report


async def main():
    """Main execution flow"""
    
    # Initialize Fusion Agent
    fusion = FusionAgent()
    
    # Execute sensor fusion for a specific sector
    final_report = await fusion.execute_fusion("Alpha Sector")
    
    # Display results
    print("\n\n" + "#"*70)
    print("🚀 FINAL A2A ARTIFACT (Fusion Report)")
    print("#"*70)
    print(final_report.model_dump_json(indent=2))
    
    print("\n" + "-"*70)
    print("📊 TARGET DATA SUMMARY")
    print("-"*70)
    target = final_report.targets[0]
    print(f"Target Type:      {target.target_type}")
    print(f"Confidence:       {target.confidence * 100:.2f}%")
    print(f"Position (X, Y):  ({target.x_pos}m, {target.y_pos}m)")
    print(f"Fusion Report ID: {final_report.fusion_id}")
    print("-"*70 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())