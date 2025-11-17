"""
Model Context Protocol (MCP) Tool - Data Normalization
======================================================
Simulates an MCP tool that standardizes disparate sensor data formats.
"""

from models import RadarData, VisualData, NormalizedTarget
import math


def data_normalization_tool(radar_data: RadarData, visual_data: VisualData) -> NormalizedTarget:
    """
    MCP Tool: Normalizes disparate sensor data into a standardized format.
    
    Takes raw radar data (polar coordinates) and visual data (classification)
    and outputs a unified NormalizedTarget with Cartesian coordinates.
    
    Args:
        radar_data: Raw radar sensor data in polar format
        visual_data: Raw visual sensor data with classification
        
    Returns:
        NormalizedTarget: Standardized target information
    """
    print("   [MCP Tool] 🔧 Executing data normalization logic...")
    
    # =========================================================================
    # STEP 1: Convert polar coordinates to Cartesian (simplified)
    # =========================================================================
    range_m = radar_data.range_meters
    azimuth_rad = math.radians(radar_data.azimuth_degrees)
    
    # Standard polar to Cartesian conversion
    # X = R * cos(θ), Y = R * sin(θ)
    x = range_m * math.cos(azimuth_rad)
    y = range_m * math.sin(azimuth_rad)
    
    # =========================================================================
    # STEP 2: Normalize classification and confidence
    # =========================================================================
    confidence = visual_data.certainty_percent / 100.0  # Convert 0-100% to 0.0-1.0
    target_type = visual_data.classification.upper()
    
    print(f"   [MCP Tool] ✓ Normalized position: ({round(x, 2)}, {round(y, 2)}) meters")
    print(f"   [MCP Tool] ✓ Confidence: {confidence:.2%}")
    
    # =========================================================================
    # STEP 3: Return standardized model
    # =========================================================================
    return NormalizedTarget(
        x_pos=round(x, 2),
        y_pos=round(y, 2),
        target_type=target_type,
        confidence=confidence
    )