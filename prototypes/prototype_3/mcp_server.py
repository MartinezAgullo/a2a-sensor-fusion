"""
MCP Server - Data Normalization Tool
=====================================
Real MCP server implementation using the official FastMCP SDK.
Provides data normalization as an MCP tool that can be called via stdio.

This replaces the simple mcp_tool.py of prototype 2 with a proper MCP server.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import math
import json

# Initialize the FastMCP server
mcp = FastMCP("SensorDataNormalizationServer")


@mcp.tool()
def normalize_sensor_data(
    radar_range_meters: float,
    radar_azimuth_degrees: float,
    visual_classification: str,
    visual_certainty_percent: int
) -> Dict[str, Any]:
    """
    Normalizes disparate sensor data into a standardized format.
    
    Takes raw radar data (polar coordinates) and visual data (classification)
    and outputs a unified target representation with Cartesian coordinates.
    
    Args:
        radar_range_meters: Target range from radar in meters
        radar_azimuth_degrees: Target azimuth angle from radar in degrees (0-360)
        visual_classification: Target type from visual sensor (drone, aircraft, vessel, unknown)
        visual_certainty_percent: Classification certainty from visual sensor (0-100%)
        
    Returns:
        A dictionary containing:
        - x_pos: Normalized X coordinate in meters (Cartesian)
        - y_pos: Normalized Y coordinate in meters (Cartesian)
        - target_type: Standardized target classification (uppercase)
        - confidence: Normalized confidence score (0.0-1.0)
        - metadata: Additional processing information
    """
    
    # =========================================================================
    # STEP 1: Convert polar coordinates to Cartesian
    # =========================================================================
    azimuth_rad = math.radians(radar_azimuth_degrees)
    
    # Standard polar to Cartesian conversion
    # X = R × cos(θ), Y = R × sin(θ)
    x_pos = radar_range_meters * math.cos(azimuth_rad)
    y_pos = radar_range_meters * math.sin(azimuth_rad)
    
    # =========================================================================
    # STEP 2: Normalize classification and confidence
    # =========================================================================
    confidence = visual_certainty_percent / 100.0  # Convert 0-100% to 0.0-1.0
    target_type = visual_classification.upper()
    
    # =========================================================================
    # STEP 3: Return standardized format
    # =========================================================================
    return {
        "x_pos": round(x_pos, 2),
        "y_pos": round(y_pos, 2),
        "target_type": target_type,
        "confidence": round(confidence, 2),
        "metadata": {
            "original_polar": {
                "range_meters": radar_range_meters,
                "azimuth_degrees": radar_azimuth_degrees
            },
            "processing_method": "polar_to_cartesian_conversion",
            "mcp_server": "SensorDataNormalizationServer"
        }
    }


@mcp.tool()
def validate_sensor_data(
    radar_range_meters: float,
    radar_azimuth_degrees: float,
    visual_certainty_percent: int
) -> Dict[str, Any]:
    """
    Validates sensor data for consistency and quality.
    
    Args:
        radar_range_meters: Target range from radar in meters
        radar_azimuth_degrees: Target azimuth angle from radar in degrees
        visual_certainty_percent: Classification certainty from visual sensor
        
    Returns:
        Validation results with quality metrics and warnings
    """
    warnings = []
    quality_score = 100.0
    
    # Check radar range validity
    if radar_range_meters < 0:
        warnings.append("Negative radar range detected - invalid")
        quality_score -= 50
    elif radar_range_meters > 10000:
        warnings.append("Radar range exceeds typical detection limit")
        quality_score -= 10
    
    # Check azimuth validity
    if not (0 <= radar_azimuth_degrees <= 360):
        warnings.append("Azimuth outside valid range (0-360 degrees)")
        quality_score -= 30
    
    # Check visual certainty
    if visual_certainty_percent < 50:
        warnings.append("Low visual classification confidence")
        quality_score -= 20
    elif visual_certainty_percent < 70:
        warnings.append("Moderate visual classification confidence")
        quality_score -= 10
    
    return {
        "is_valid": len(warnings) == 0 or quality_score > 30,
        "quality_score": max(0, quality_score),
        "warnings": warnings,
        "recommendation": "ACCEPT" if quality_score > 70 else "REVIEW" if quality_score > 30 else "REJECT"
    }


# Run the MCP server using stdio transport
if __name__ == "__main__":
    print("🚀 Starting MCP Data Normalization Server...")
    print("📡 Transport: stdio")
    print("🔧 Tools available:")
    print("   - normalize_sensor_data")
    print("   - validate_sensor_data")
    mcp.run(transport='stdio')