"""
Pydantic models for request/response validation and data structures.
"""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ── Request Models ──────────────────────────────────────────────

class ProjectRequirements(BaseModel):
    """Greenfield mode input: project requirements."""
    description: str = Field(..., min_length=10, description="Project description text")
    expected_users: Optional[str] = Field("medium", description="Expected user load: low/medium/high")
    scalability: Optional[str] = Field("medium", description="Scalability need: low/medium/high")
    complexity: Optional[str] = Field("medium", description="Project complexity: low/medium/high")
    constraints: Optional[list[str]] = Field(default_factory=list, description="Technical constraints")


# ── Analysis Result Models ──────────────────────────────────────

class ModuleMetrics(BaseModel):
    """Per-module coupling metrics."""
    module: str
    fan_in: int = 0
    fan_out: int = 0
    instability: float = 0.0


class MetricsResult(BaseModel):
    """Aggregate metrics from dependency graph analysis."""
    avg_instability: float = Field(..., ge=0.0, le=1.0)
    dependency_density: float = Field(..., ge=0.0, le=1.0)
    total_modules: int = Field(..., ge=0)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    per_module: Optional[list[ModuleMetrics]] = Field(default_factory=list)


class GraphData(BaseModel):
    """Serialized dependency graph for frontend visualization."""
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)


# ── Suggestion Models ──────────────────────────────────────────

class ArchitectureSuggestion(BaseModel):
    """Architecture recommendation from the Planning Agent."""
    suggested_architecture: str
    reason: str
    pattern_description: Optional[str] = ""
    pros: Optional[list[str]] = Field(default_factory=list)
    cons: Optional[list[str]] = Field(default_factory=list)


# ── Response Models ────────────────────────────────────────────

class BrownfieldAnalysis(BaseModel):
    """Analysis section of brownfield response."""
    metrics: MetricsResult
    risk_score: float


class GreenfieldAnalysis(BaseModel):
    """Analysis section of greenfield response."""
    scalability: str
    complexity: str


class BrownfieldResponse(BaseModel):
    """Full response for POST /brownfield."""
    analysis: BrownfieldAnalysis
    suggestion: ArchitectureSuggestion
    graph: Optional[GraphData] = None
    agent_logs: Optional[list[dict]] = Field(default_factory=list)


class GreenfieldResponse(BaseModel):
    """Full response for POST /greenfield."""
    analysis: GreenfieldAnalysis
    suggestion: ArchitectureSuggestion
    agent_logs: Optional[list[dict]] = Field(default_factory=list)
