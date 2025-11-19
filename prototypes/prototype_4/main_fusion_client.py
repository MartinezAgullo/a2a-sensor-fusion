"""
Prototype 4: Fusion Agent (A2A Client)
=======================================
Full A2A SDK integration using:
- A2ACardResolver for agent discovery
- A2AClient for standardized communication
- SendMessageRequest for structured requests
- Streaming support via send_message_streaming

This orchestrates multiple sensor agents and produces fusion reports.
"""

import httpx
import json
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any

from a2a.client import A2ACardResolver, ClientFactory
from a2a.types import (
    AgentCard,
    TransportProtocol,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

from models import (
    RadarData, 
    VisualData, 
    NormalizedTarget, 
    FusionReport,
    SensorTaskParams
)
from mcp_client import MCPClient


# ============================================================================
# FUSION AGENT (A2A Client)
# ============================================================================

class FusionAgent:
    """
    Prototype 4: Fusion Agent using official A2A SDK.
    
    Orchestrates:
    1. Agent discovery via A2ACardResolver
    2. Task delegation via A2AClient
    3. Data normalization via MCP
    4. Report generation
    """
    
    def __init__(
        self,
        radar_url: str = "http://localhost:8001",
        visual_url: str = "http://localhost:8002"
    ):
        self.radar_url = radar_url
        self.visual_url = visual_url
        
        # Will be populated during discovery
        self.radar_card: AgentCard = None
        self.visual_card: AgentCard = None
        
        # MCP client for normalization
        self.mcp_client = MCPClient()
    
    async def discover_agents(self, httpx_client: httpx.AsyncClient) -> None:
        """
        Phase 1: Discover available agents using A2ACardResolver.
        
        A2ACardResolver automatically:
        - Fetches agent cards from /.well-known/ai-agent.json
        - Validates card structure
        - Handles extended cards (if supported)
        """
        print("\n" + "="*70)
        print("🔍 AGENT DISCOVERY PHASE (A2A SDK)")
        print("="*70)
        
        # Discover Radar Agent
        print(f"\n[Discovery] Querying Radar Agent at {self.radar_url}...")
        try:
            radar_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=self.radar_url
            )
            self.radar_card = await radar_resolver.get_agent_card()
            print(f"[Discovery] ✓ {self.radar_card.name} v{self.radar_card.version}")
            print(f"[Discovery]   Skills: {', '.join([s.name for s in self.radar_card.skills])}")
            print(f"[Discovery]   Streaming: {self.radar_card.capabilities.streaming}")
        except Exception as e:
            print(f"[Discovery] ✗ Failed to discover Radar Agent: {e}")
            raise
        
        # Discover Visual Agent
        print(f"\n[Discovery] Querying Visual Agent at {self.visual_url}...")
        try:
            visual_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=self.visual_url
            )
            self.visual_card = await visual_resolver.get_agent_card()
            print(f"[Discovery] ✓ {self.visual_card.name} v{self.visual_card.version}")
            print(f"[Discovery]   Skills: {', '.join([s.name for s in self.visual_card.skills])}")
            print(f"[Discovery]   Streaming: {self.visual_card.capabilities.streaming}")
        except Exception as e:
            print(f"[Discovery] ✗ Failed to discover Visual Agent: {e}")
            raise
        
        print(f"\n[Discovery] 📊 Discovery Complete: 2 agents ready")
        print("="*70)
    
    async def query_radar_agent(
        self, 
        httpx_client: httpx.AsyncClient,
        sector_id: str
    ) -> RadarData:
        """
        Query Radar Agent using ClientFactory (modern A2A SDK API).
        
        Uses:
        - ClientFactory for creating clients
        - create_text_message_object for messages
        - JSON-RPC transport
        """
        print(f"\n[Fusion Agent] → Contacting Radar Agent (Port 8001)...")
        
        # Create task parameters
        task_params = SensorTaskParams(
            sector_id=sector_id,
            request_type="track",
            priority=8
        )
        
        # Create client using ClientFactory (modern API)
        client = ClientFactory.create_client_from_agent_card(
            agent_card=self.radar_card,
            httpx_client=httpx_client,
            transport_protocol=TransportProtocol.JSON_RPC,
        )
        
        # Create message using utility function
        from a2a.client import create_text_message_object
        message = create_text_message_object(task_params.model_dump_json())
        
        # Send message
        response = await client.send_message(message)
        
        # Parse response
        response_text = response.result.message.parts[0].text
        radar_data = RadarData.model_validate_json(response_text)
        
        return radar_data
    
    async def query_visual_agent(
        self, 
        httpx_client: httpx.AsyncClient,
        sector_id: str
    ) -> VisualData:
        """
        Query Visual Agent using ClientFactory (modern A2A SDK API).
        """
        print(f"[Fusion Agent] → Contacting Visual Agent (Port 8002)...")
        
        # Create task parameters
        task_params = SensorTaskParams(
            sector_id=sector_id,
            request_type="classify",
            priority=8
        )
        
        # Create client using ClientFactory (modern API)
        client = ClientFactory.create_client_from_agent_card(
            agent_card=self.visual_card,
            httpx_client=httpx_client,
            transport_protocol=TransportProtocol.JSON_RPC,
        )
        
        # Create message using utility function
        from a2a.client import create_text_message_object
        message = create_text_message_object(task_params.model_dump_json())
        
        # Send message
        response = await client.send_message(message)
        
        # Parse response
        response_text = response.result.message.parts[0].text
        visual_data = VisualData.model_validate_json(response_text)
        
        return visual_data
    
    async def execute_fusion(self, sector_id: str) -> FusionReport:
        """
        Execute complete sensor fusion workflow.
        
        Workflow:
        1. Discover agents (A2A)
        2. Query sensors (A2A)
        3. Validate data (MCP)
        4. Normalize data (MCP)
        5. Generate report (Fusion)
        """
        async with httpx.AsyncClient(timeout=30.0) as httpx_client:
            
            # ================================================================
            # PHASE 1: AGENT DISCOVERY
            # ================================================================
            await self.discover_agents(httpx_client)
            
            # ================================================================
            # PHASE 2: A2A TASK DELEGATION
            # ================================================================
            print("\n" + "="*70)
            print("🎯 FUSION AGENT ORCHESTRATION STARTING")
            print("="*70)
            print(f"\n[Fusion Agent] 📤 Delegating tasks to sensor agents...")
            print(f"[Fusion Agent] Target Sector: {sector_id}")
            
            # Query both sensors in parallel
            radar_data = await self.query_radar_agent(httpx_client, sector_id)
            visual_data = await self.query_visual_agent(httpx_client, sector_id)
            
            print(f"\n[Fusion Agent] ✅ Received raw data from both sensors")
            print(f"[Fusion Agent] Radar: {radar_data.range_meters}m @ {radar_data.azimuth_degrees}°")
            print(f"[Fusion Agent] Visual: {visual_data.classification.upper()} ({visual_data.certainty_percent}%)")
            
            # ================================================================
            # PHASE 3: MCP PROCESSING
            # ================================================================
            print(f"\n[Fusion Agent] 🔄 Transitioning to MCP processing...")
            await self.mcp_client.start()
            
            try:
                # Validate data quality
                validation = await self.mcp_client.validate_sensor_data(
                    radar_data, 
                    visual_data
                )
                
                # Normalize data
                normalized_target = await self.mcp_client.normalize_sensor_data(
                    radar_data,
                    visual_data
                )
                
            finally:
                await self.mcp_client.stop()
            
            # ================================================================
            # PHASE 4: FUSION REPORT GENERATION
            # ================================================================
            fusion_report = FusionReport(
                sector_id=sector_id,
                targets=[normalized_target],
                summary=(
                    f"Track successful for {sector_id}. "
                    f"Detected 1 {normalized_target.target_type} target "
                    f"at position ({normalized_target.x_pos}, {normalized_target.y_pos}) "
                    f"with {normalized_target.confidence:.0%} confidence."
                ),
                quality_score=validation["quality_score"],
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            print(f"\n[Fusion Agent] ✅ Successfully generated Fusion Report")
            
            return fusion_report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """
    Main execution flow for Prototype 4.
    Demonstrates full A2A SDK + MCP integration.
    """
    
    # Initialize Fusion Agent
    fusion = FusionAgent()
    
    # Execute sensor fusion
    final_report = await fusion.execute_fusion("Alpha Sector")
    
    # Display results
    print("\n\n" + "#"*70)
    print("🚀 FINAL FUSION REPORT")
    print("#"*70)
    print(final_report.model_dump_json(indent=2))
    
    print("\n" + "-"*70)
    print("📊 TARGET DATA SUMMARY")
    print("-"*70)
    target = final_report.targets[0]
    print(f"Target Type:       {target.target_type}")
    print(f"Confidence:        {target.confidence * 100:.2f}%")
    print(f"Position (X, Y):   ({target.x_pos}m, {target.y_pos}m)")
    print(f"Quality Score:     {final_report.quality_score:.1f}/100")
    print(f"Fusion Report ID:  {final_report.fusion_id}")
    print(f"Timestamp:         {final_report.timestamp}")
    print("-"*70 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())