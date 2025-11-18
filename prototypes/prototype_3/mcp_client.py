"""
MCP Client - For Fusion Agent
==============================
Simplified client for calling the MCP normalization tool.
We use a direct async function wrapper that prepares
for future MCP server integration.
"""

from typing import Dict, Any
from models import RadarData, VisualData, NormalizedTarget
import math


class MCPClient:
    """
    Simplified MCP Client for sensor data normalization.
    
    Same interface as a real MCP client would,
    but implements the logic directly for simplicity.
    
    Future: Can be replaced with real stdio/HTTP MCP client.
    """
    
    def __init__(self):
        self.started = False
    
    async def start(self):
        """Initialize the MCP client"""
        print("[MCP Client] 🚀 MCP client initialized")
        self.started = True
    
    async def stop(self):
        """Cleanup the MCP client"""
        print("[MCP Client] 🛑 MCP client stopped")
        self.started = False
    
    async def normalize_sensor_data(
        self,
        radar_data: RadarData,
        visual_data: VisualData
    ) -> NormalizedTarget:
        """
        MCP Tool: Normalizes disparate sensor data into standardized format.
        
        Args:
            radar_data: Raw radar sensor data (polar coordinates)
            visual_data: Raw visual sensor data (classification)
            
        Returns:
            NormalizedTarget: Standardized target information
        """
        if not self.started:
            raise RuntimeError("MCP Client not started. Call start() first.")
        
        print("\n[MCP Client] 🔧 Calling normalize_sensor_data tool...")
        
        # =====================================================================
        # STEP 1: Convert polar coordinates to Cartesian
        # =====================================================================
        range_m = radar_data.range_meters
        azimuth_rad = math.radians(radar_data.azimuth_degrees)
        
        # Standard polar to Cartesian conversion
        # X = R × cos(θ), Y = R × sin(θ)
        x = range_m * math.cos(azimuth_rad)
        y = range_m * math.sin(azimuth_rad)
        
        # =====================================================================
        # STEP 2: Normalize classification and confidence
        # =====================================================================
        confidence = visual_data.certainty_percent / 100.0  # Convert to 0.0-1.0
        target_type = visual_data.classification.upper()
        
        print(f"[MCP Client] ✓ Normalized position: ({round(x, 2)}, {round(y, 2)}) meters")
        print(f"[MCP Client] ✓ Confidence: {confidence:.2%}")
        
        # =====================================================================
        # STEP 3: Return standardized model
        # =====================================================================
        return NormalizedTarget(
            x_pos=round(x, 2),
            y_pos=round(y, 2),
            target_type=target_type,
            confidence=confidence
        )
    
    async def validate_sensor_data(
        self,
        radar_data: RadarData,
        visual_data: VisualData
    ) -> Dict[str, Any]:
        """
        MCP Tool: Validates sensor data quality.
        
        Args:
            radar_data: Raw radar sensor data
            visual_data: Raw visual sensor data
            
        Returns:
            Validation results with quality metrics
        """
        if not self.started:
            raise RuntimeError("MCP Client not started. Call start() first.")
        
        print("\n[MCP Client] 🔍 Validating sensor data quality...")
        
        warnings = []
        quality_score = 100.0
        
        # Check radar range validity
        if radar_data.range_meters < 0:
            warnings.append("Negative radar range detected - invalid")
            quality_score -= 50
        elif radar_data.range_meters > 10000:
            warnings.append("Radar range exceeds typical detection limit")
            quality_score -= 10
        
        # Check azimuth validity
        if not (0 <= radar_data.azimuth_degrees <= 360):
            warnings.append("Azimuth outside valid range (0-360 degrees)")
            quality_score -= 30
        
        # Check visual certainty
        if visual_data.certainty_percent < 50:
            warnings.append("Low visual classification confidence")
            quality_score -= 20
        elif visual_data.certainty_percent < 70:
            warnings.append("Moderate visual classification confidence")
            quality_score -= 10
        
        recommendation = "ACCEPT" if quality_score > 70 else "REVIEW" if quality_score > 30 else "REJECT"
        
        result = {
            "is_valid": len(warnings) == 0 or quality_score > 30,
            "quality_score": max(0, quality_score),
            "warnings": warnings,
            "recommendation": recommendation
        }
        
        print(f"[MCP Client] Quality Score: {result['quality_score']:.1f}/100")
        print(f"[MCP Client] Recommendation: {result['recommendation']}")
        
        if result["warnings"]:
            print(f"[MCP Client] ⚠️  Warnings: {', '.join(result['warnings'])}")
        
        return result