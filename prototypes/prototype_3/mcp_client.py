"""
MCP Client - For Fusion Agent
==============================
Real MCP client that calls the FastMCP-based server (mcp_server.py).

The FusionAgent uses this client to:
- validate_sensor_data  -> calls MCP tool 'validate_sensor_data'
- normalize_sensor_data -> calls MCP tool 'normalize_sensor_data'
"""

from __future__ import annotations

import json
from pathlib import Path
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional

from fastmcp import Client as FastMCPClient  # FastMCP client
from models import RadarData, VisualData, NormalizedTarget


class MCPClient:
    """
    MCP Client for sensor data normalization.

    Connects to the FastMCP server defined in `mcp_server.py` 
    and calls its tools via the MCP protocol (stdio).
    """

    def __init__(self, server_target: Optional[str] = None) -> None:
        """
        Args:
            server_target:
                What FastMCP should connect to.

                - If None (default), we resolve the local `mcp_server.py`
                  file next to this client and use that as the target
                  (FastMCP will use stdio to run it as a subprocess).
                - You can also pass a URL (e.g. "http://localhost:8000/mcp")
                  if you later run the server with HTTP transport.
        """
        if server_target is None:
            server_path = Path(__file__).with_name("mcp_server.py")
            self.server_target = str(server_path)
        else:
            self.server_target = server_target

        self.started: bool = False
        self._exit_stack: Optional[AsyncExitStack] = None
        self._client: Optional[FastMCPClient] = None

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def start(self) -> None:
        """Initialize the MCP client and connect to the MCP server."""
        if self.started:
            # Idempotent: allow multiple start() calls safely.
            return

        print(f"[MCP Client] 🚀 Connecting to MCP server at {self.server_target}...")

        self._exit_stack = AsyncExitStack()

        # Create the FastMCP client; it is an async context manager.
        base_client = FastMCPClient(self.server_target)

        # Enter the client context and keep it open until stop() is called.
        self._client = await self._exit_stack.enter_async_context(base_client)

        # Ensure the MCP handshake is complete.
        await self._client.initialize()

        self.started = True
        print("[MCP Client] ✅ MCP client initialized and ready")

    async def stop(self) -> None:
        """Cleanup the MCP client connection."""
        if not self.started:
            return

        print("[MCP Client] 🛑 Shutting down MCP client...")

        try:
            if self._exit_stack is not None:
                await self._exit_stack.aclose()
        finally:
            self._exit_stack = None
            self._client = None
            self.started = False

        print("[MCP Client] ✅ MCP client stopped")

    # -------------------------------------------------------------------------
    # Helper to normalize FastMCP tool results
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_text_from_result(result: Any) -> str:
        """
        FastMCP's `call_tool` typically returns either:

        - A list of content parts: result[0].text
        - Or a CallToolResult-like object with `.content[0].text`

        This helper tries to normalize both cases and returns the text body.
        """
        # Case 1: result is a CallToolResult with `.content`
        if hasattr(result, "content"):
            content_list = result.content
        else:
            # Case 2: result is already a sequence of parts
            content_list = result

        try:
            first_part = content_list[0]
        except (TypeError, IndexError):
            raise RuntimeError("MCP tool returned an empty result")

        if hasattr(first_part, "text"):
            return first_part.text
        # Fallback: stringify whatever we got
        return str(first_part)

    # -------------------------------------------------------------------------
    # MCP Tools
    # -------------------------------------------------------------------------

    async def normalize_sensor_data(
        self,
        radar_data: RadarData,
        visual_data: VisualData,
    ) -> NormalizedTarget:
        """
        Call MCP tool: normalize_sensor_data

        Args:
            radar_data: Raw radar sensor data (polar coordinates)
            visual_data: Raw visual sensor data (classification)

        Returns:
            NormalizedTarget: Standardized target information
        """
        if not self.started or self._client is None:
            raise RuntimeError("MCP Client not started. Call start() first.")

        print("\n[MCP Client] 🔧 Calling MCP tool 'normalize_sensor_data'...")

        args = {
            "radar_range_meters": radar_data.range_meters,
            "radar_azimuth_degrees": radar_data.azimuth_degrees,
            "visual_classification": visual_data.classification,
            "visual_certainty_percent": visual_data.certainty_percent,
        }

        # Call the MCP tool on the server
        result = await self._client.call_tool("normalize_sensor_data", args)

        # Extract JSON text from the MCP result and parse it
        text_payload = self._extract_text_from_result(result)
        data = json.loads(text_payload)

        # Log a small summary
        print(
            f"[MCP Client] ✓ Normalized position: "
            f"({data['x_pos']}, {data['y_pos']}) meters"
        )
        print(f"[MCP Client] ✓ Confidence: {data['confidence']:.2f}")
        print(f"[MCP Client] ✓ Target type: {data['target_type']}")

        # Build the Pydantic model that the rest of the system expects
        return NormalizedTarget(
            x_pos=data["x_pos"],
            y_pos=data["y_pos"],
            target_type=data["target_type"],
            confidence=data["confidence"],
        )

    async def validate_sensor_data(
        self,
        radar_data: RadarData,
        visual_data: VisualData,
    ) -> Dict[str, Any]:
        """
        Call MCP tool: validate_sensor_data

        Args:
            radar_data: Raw radar sensor data
            visual_data: Raw visual sensor data

        Returns:
            Validation results with quality metrics, as a plain dict.
        """
        if not self.started or self._client is None:
            raise RuntimeError("MCP Client not started. Call start() first.")

        print("\n[MCP Client] 🔍 Calling MCP tool 'validate_sensor_data'...")

        args = {
            "radar_range_meters": radar_data.range_meters,
            "radar_azimuth_degrees": radar_data.azimuth_degrees,
            "visual_certainty_percent": visual_data.certainty_percent,
        }

        result = await self._client.call_tool("validate_sensor_data", args)

        text_payload = self._extract_text_from_result(result)
        validation = json.loads(text_payload)

        # Logging, mirroring the previous in-process implementation
        quality = validation.get("quality_score")
        recommendation = validation.get("recommendation")
        warnings = validation.get("warnings") or []

        if quality is not None:
            print(f"[MCP Client] Quality Score: {quality:.1f}/100")
        if recommendation is not None:
            print(f"[MCP Client] Recommendation: {recommendation}")
        if warnings:
            print(f"[MCP Client] ⚠️  Warnings: {', '.join(warnings)}")

        return validation
