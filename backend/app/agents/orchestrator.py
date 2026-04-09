"""
Orchestrator: coordinates the agent pipeline.
Runs agents sequentially, passing shared AgentContext through each.
"""
from __future__ import annotations
from datetime import datetime, timezone
from .base import BaseAgent, AgentContext
from .analysis_agent import AnalysisAgent
from .planning_agent import PlanningAgent


class Orchestrator:
    """
    Pipeline orchestrator that runs agents in order:
      1. AnalysisAgent  — diagnoses the system
      2. PlanningAgent  — recommends architecture

    Extensible: append new agents to self.agents list.
    """

    def __init__(self) -> None:
        self.agents: list[BaseAgent] = [
            AnalysisAgent(),
            PlanningAgent(),
        ]

    async def run(self, context: AgentContext) -> AgentContext:
        """Execute the full agent pipeline."""
        context.agent_logs.append({
            "agent": "Orchestrator",
            "message": f"Pipeline started for mode='{context.mode}'",
            "level": "info",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        for agent in self.agents:
            context.agent_logs.append({
                "agent": agent.name,
                "message": "Agent started",
                "level": "info",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            try:
                context = await agent.run(context)
                context.agent_logs.append({
                    "agent": agent.name,
                    "message": "Agent completed successfully",
                    "level": "info",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                error_msg = f"Agent failed: {str(e)}"
                context.agent_logs.append({
                    "agent": agent.name,
                    "message": error_msg,
                    "level": "error",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                context.errors.append(f"{agent.name}: {error_msg}")
                # Continue pipeline even if one agent fails — partial results

        context.agent_logs.append({
            "agent": "Orchestrator",
            "message": "Pipeline completed",
            "level": "info",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return context
