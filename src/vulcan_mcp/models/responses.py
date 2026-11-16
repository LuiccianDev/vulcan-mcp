"""Pydantic v2 data models for Vulcan MCP."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VulcanBaseResponse(BaseModel):
    """Base response model for Vulcan MCP tools."""

    status: str = Field(default="ok", description="Status code ('ok' or 'error')")
    error: Optional[str] = Field(default=None, description="Error message if status is 'error'")


class VulcanPingResponse(VulcanBaseResponse):
    """Response model for system ping."""

    message: Optional[str] = None
    protocol_version: Optional[int] = None
    vulcan_version: Optional[str] = None


class VulcanInventoryResponse(VulcanBaseResponse):
    """Response model for project inventory."""

    project: Optional[str] = None
    block_models: List[str] = Field(default_factory=list)
    triangulations: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    design_databases: List[str] = Field(default_factory=list)
    grids: List[str] = Field(default_factory=list)


class CutoffInterval(BaseModel):
    """Cumulative grade-tonnage metrics above a specific cutoff."""

    cutoff: float
    blocks_above: int
    volume: float
    tonnes: float
    mean_grade: float
    metal_content: float


class GradeTonnageResponse(VulcanBaseResponse):
    """Response model for block model grade-tonnage curve evaluation."""

    model_name: Optional[str] = None
    variable: Optional[str] = None
    density: Optional[float] = None
    total_blocks: Optional[int] = None
    total_volume: Optional[float] = None
    total_tonnes: Optional[float] = None
    overall_mean_grade: Optional[float] = None
    intervals: List[CutoffInterval] = Field(default_factory=list)


class BlockModelStatsResponse(VulcanBaseResponse):
    """Response model for block model summary and statistics."""

    model_name: Optional[str] = None
    schema_info: Optional[Dict[str, Any]] = None
    extent: Optional[Dict[str, Any]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    stats: Optional[Dict[str, Any]] = None


class ProfilePoint(BaseModel):
    """Sample point along an elevation profile."""

    station: float
    x: float
    y: float
    z: Optional[float] = None


class ElevationProfileResponse(VulcanBaseResponse):
    """Response model for longitudinal elevation profile across a triangulation."""

    triangulation: Optional[str] = None
    total_length: Optional[float] = None
    step: Optional[float] = None
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None
    points: List[ProfilePoint] = Field(default_factory=list)


class TriangulationResponse(VulcanBaseResponse):
    """Response model for 3D triangulation/solid query."""

    triangulation: Optional[str] = None
    triangles: Optional[int] = None
    volume: Optional[float] = None
    surface_area: Optional[float] = None
    extent: Optional[Dict[str, float]] = None


class DrillholeAuditResponse(VulcanBaseResponse):
    """Response model for drillhole database audit."""

    database: Optional[str] = None
    hole_count: Optional[int] = None
    tables: Optional[List[str]] = None
    holes: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None


class DesignCadResponse(VulcanBaseResponse):
    """Response model for CAD layers and objects."""

    database: Optional[str] = None
    layer_count: Optional[int] = None
    layers: Optional[List[str]] = None
    objects: Optional[List[Dict[str, Any]]] = None


class LegendResponse(VulcanBaseResponse):
    """Response model for Vulcan colour legends (.scd)."""

    legend_file: Optional[str] = None
    field: Optional[str] = None
    intervals: Optional[List[Dict[str, Any]]] = None


class CanvasResponse(VulcanBaseResponse):
    """Response model for Envisage canvas and screenshot operations."""

    screenshot_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    view_direction: Optional[List[float]] = None


class ExecuteCodeResponse(VulcanBaseResponse):
    """Response model for executing Python in Vulcan."""

    stdout: Optional[str] = None
    stderr: Optional[str] = None
    result: Optional[Any] = None
