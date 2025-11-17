"""
Fusion Agent (A2A Client / Orchestrator)
=========================================
Main client agent that:
1. Discovers available sensor agents via A2A Agent Cards
2. Sends A2A tasks to remote Sensor Agents
3. Collects disparate sensor data
4. Uses MCP client to call normalization tool
5. Generates final A2A Artifact (fusion report)
"""

import httpx
import uuid
from models import (
    A2ATask, RadarData, VisualData, A2AArtifact, 
    AgentCard, AgentRegistry
)
from mcp_client import MCPClient


class FusionAgent:
    """
    Client Agent that orchestrates sensor fusion using A2A and MCP protocols.
    """
    
    def __init__(self, 
                 radar_url: str = "http://localhost:8001", 
                 visual_url: str = "http://localhost:8002",
                 use_discovery: bool = True):
        self.radar_url = radar_url
        self.visual_url = visual_url
        self.use_discovery = use_discovery
        
        # Agent registry for discovered agents
        self.registry = AgentRegistry()
        
        # MCP client for normalization
        self.mcp_client = MCPClient()
    
    async def discover_agents(self) -> None:
        """
        Discover available agents by querying their /card endpoints.
        Validates capabilities and registers agents in the local registry.
        """
        print("\n" + "="*70)
        print("🔍 AGENT DISCOVERY PHASE")
        print("="*70)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Discover Radar Agent
            print(f"\n[Discovery] Querying Radar Agent at {self.radar_url}/card...")
            try:
                radar_response = await client.get(f"{self.radar_url}/card")
                radar_card = AgentCard(**radar_response.json())
                self.registry.register_agent("radar_agent", radar_card)
                print(f"[Discovery] ✓ {radar_card.name} v{radar_card.version}")
                print(f"[Discovery]   Skills: {', '.join([s.name for s in radar_card.skills])}")
            except Exception as e:
                print(f"[Discovery] ✗ Failed to discover Radar Agent: {e}")
            
            # Discover Visual Agent
            print(f"\n[Discovery] Querying Visual Agent at {self.visual_url}/card...")
            try:
                visual_response = await client.get(f"{self.visual_url}/card")
                visual_card = AgentCard(**visual_response.json())
                self.registry.register_agent("visual_agent", visual_card)
                print(f"[Discovery] ✓ {visual_card.name} v{visual_card.version}")
                print(f"[Discovery]   Skills: {', '.join([s.name for s in visual_card.skills])}")
            except Exception as e:
                print(f"[Discovery] ✗ Failed to discover Visual Agent: {e}")
        
        # Summary
        print(f"\n[Discovery] 📊 Discovery Complete: {len(self.registry.agents)} agents registered")
        
        # Validate required skills
        radar_agents = self.registry.find_agents_by_skill("radar_detection")
        visual_agents = self.registry.find_agents_by_skill("visual_classification")
        
        if not radar_agents:
            print("[Discovery] ⚠️  Warning: No agents with 'radar_detection' skill found")
        if not visual_agents:
            print("[Discovery] ⚠️  Warning: No agents with 'visual_classification' skill found")
        
        print("="*70)
        
    async def execute_fusion(self, sector: str) -> A2AArtifact:
        """
        Execute the full sensor fusion workflow.

        Args:
            sector: Surveillance sector identifier
            
        Returns:
            A2AArtifact: Final fusion report with normalized target data
        """
        
        # =====================================================================
        # OPTIONAL AGENT DISCOVERY
        # =====================================================================
        if self.use_discovery and len(self.registry.agents) == 0:
            await self.discover_agents()
        
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
        # MCP CLIENT - Start and validate data
        # =====================================================================
        print("\n[Fusion Agent] 🔄 Transitioning to MCP Client...")
        await self.mcp_client.start()
        
        try:
            # Optional: Validate data quality first
            validation = await self.mcp_client.validate_sensor_data(radar_data, visual_data)
            
            if validation["recommendation"] == "REJECT":
                print(f"[Fusion Agent] ⚠️  Warning: Poor data quality (score: {validation['quality_score']})")
            
            # =====================================================================
            # MCP STEP: Normalize the disparate sensor data
            # =====================================================================
            normalized_target = await self.mcp_client.normalize_sensor_data(
                radar_data, 
                visual_data
            )
        finally:
            await self.mcp_client.stop()
        
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
    """Main execution flow with Phase 2 enhancements"""
    
    # Initialize Fusion Agent with discovery enabled
    fusion = FusionAgent(use_discovery=True)
    
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
    
    # Show discovered agents
    if fusion.registry.agents:
        print("\n" + "-"*70)
        print("🔍 DISCOVERED AGENTS")
        print("-"*70)
        for agent_id, card in fusion.registry.agents.items():
            print(f"{card.name} v{card.version}")
            print(f"  URL: {card.url}")
            print(f"  Skills: {', '.join([s.id for s in card.skills])}")
        print("-"*70)
    
    print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())