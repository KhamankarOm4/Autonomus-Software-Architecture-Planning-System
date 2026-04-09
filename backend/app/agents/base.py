"""
Agent base class and shared AgentContext dataclass.
The agent pipeline passes an AgentContext through each agent sequentially.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Literal, Any


@dataclass
class AgentContext:
    """
    Shared state container passed through the agent pipeline.
    Each agent reads from and writes to this context.
    """
    # ── Input ──
    mode: Literal["greenfield", "brownfield"]
    requirements: Optional[Any] = None          # ProjectRequirements (greenfield)
    code_path: Optional[str] = None             # Extracted ZIP path (brownfield)

    # ── Filled by Analysis Agent ──
    dependencies: list[tuple[str, str]] = field(default_factory=list)
    graph_data: Optional[dict] = None           # {nodes: [...], edges: [...]}
    metrics: Optional[dict] = None              # MetricsResult as dict
    risk_score: Optional[float] = None
    inferred_scalability: Optional[str] = None  # greenfield
    inferred_complexity: Optional[str] = None   # greenfield
    per_module_metrics: list[dict] = field(default_factory=list)

    # ── Filled by Planning Agent ──
    suggestion: Optional[dict] = None           # ArchitectureSuggestion as dict

    # ── Observability ──
    agent_logs: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all agents in the pipeline."""

    name: str = "BaseAgent"
    description: str = "Base agent"

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentContext:
        """
        Execute agent logic. Read from context, process, write results back.
        Must return the (possibly modified) context.
        """
        ...

    def log(self, context: AgentContext, message: str, level: str = "info") -> None:
        """Append a log entry to the context."""
        from datetime import datetime, timezone
        context.agent_logs.append({
            "agent": self.name,
            "message": message,
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
