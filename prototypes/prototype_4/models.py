"""
Prototype 4: Data Models
=========================
Shared data models for A2A SDK integration.
Using Pydantic for validation alongside A2A protocol structures.
"""

from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import uuid


# ============================================================================
# RAW SENSOR DATA (Agent-specific formats)
# ============================================================================

class RadarData(BaseModel):
    """Radar sensor output: Polar coordinates"""
    range_meters: float = Field(..., description="Target range in meters")
    azimuth_degrees: float = Field(..., description="Target azimuth angle in degrees (0-360)")
    timestamp: Optional[str] = Field(default=None, description="Measurement timestamp")


class VisualData(BaseModel):
    """Visual sensor output: Classification with certainty"""
    classification: Literal["drone", "aircraft", "vessel", "unknown"] = Field(
        ..., description="Target type classification"
    )
    certainty_percent: int = Field(..., ge=0, le=100, description="Classification confidence (0-100%)")
    timestamp: Optional[str] = Field(default=None, description="Measurement timestamp")


# ============================================================================
# NORMALIZED DATA (After MCP processing)
# ============================================================================

class NormalizedTarget(BaseModel):
    """Standardized target representation after sensor fusion"""
    x_pos: float = Field(..., description="X coordinate in meters (Cartesian)")
    y_pos: float = Field(..., description="Y coordinate in meters (Cartesian)")
    target_type: str = Field(..., description="Standardized target classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Normalized confidence (0.0-1.0)")
    source_sensors: List[str] = Field(default_factory=list, description="Contributing sensors")


# ============================================================================
# FUSION REPORT (Final artifact)
# ============================================================================

class FusionReport(BaseModel):
    """Complete fusion analysis report"""
    fusion_id: str = Field(default_factory=lambda: f"RPT-{uuid.uuid4().hex[:8]}")
    sector_id: str = Field(..., description="Surveillance sector")
    targets: List[NormalizedTarget] = Field(..., description="Detected targets")
    summary: str = Field(..., description="Executive summary")
    quality_score: float = Field(default=100.0, description="Overall data quality (0-100)")
    timestamp: Optional[str] = Field(default=None, description="Report generation time")


# ============================================================================
# TASK PARAMETERS (For A2A requests)
# ============================================================================

class SensorTaskParams(BaseModel):
    """Parameters for sensor data collection task"""
    sector_id: str = Field(..., description="Target sector to scan")
    request_type: str = Field(default="track", description="Type of request (track, scan, etc.)")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1-10)")