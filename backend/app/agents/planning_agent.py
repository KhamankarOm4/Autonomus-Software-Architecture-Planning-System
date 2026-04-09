"""
Planning Agent — "The Architect"
Decides the best architecture based on the Analysis Agent's findings.
Uses the suggestion engine to apply decision rules.

Real-world analogy: An architect designing a building based on a structural engineer's report.
"""
from __future__ import annotations
from .base import BaseAgent, AgentContext


class PlanningAgent(BaseAgent):
    """
    Planning Agent that acts as a software architect.
    It decides the best architecture based on analysis.
    """

    name = "PlanningAgent"
    description = "Recommends an architecture pattern based on analysis metrics and requirements"

    async def run(self, context: AgentContext) -> AgentContext:
        self.log(context, "Starting architecture planning")

        from app.suggestion.engine import suggest_architecture

        if context.mode == "greenfield":
            suggestion = suggest_architecture(
                mode="greenfield",
                scalability=context.inferred_scalability,
                complexity=context.inferred_complexity,
            )
        elif context.mode == "brownfield":
            metrics = context.metrics or {}
            suggestion = suggest_architecture(
                mode="brownfield",
                avg_instability=metrics.get("avg_instability", 0.5),
                dependency_density=metrics.get("dependency_density", 0.5),
                total_modules=metrics.get("total_modules", 0),
                risk_score=context.risk_score or 0.5,
                per_module=context.per_module_metrics,
            )
        else:
            context.errors.append(f"PlanningAgent: Unknown mode '{context.mode}'")
            return context

        context.suggestion = suggestion
        self.log(context, f"Recommended: {suggestion['suggested_architecture']}")
        self.log(context, "Architecture planning complete")
        return context
