"""
Greenfield router: POST /greenfield
Accepts project requirements and returns architecture recommendation
via the Orchestrator → Analysis Agent → Planning Agent pipeline.
"""
from fastapi import APIRouter
from app.models import ProjectRequirements, GreenfieldResponse, GreenfieldAnalysis
from app.agents.base import AgentContext
from app.agents.orchestrator import Orchestrator

router = APIRouter()


@router.post("/greenfield", response_model=GreenfieldResponse)
async def analyze_greenfield(req: ProjectRequirements):
    """
    Analyze project requirements and suggest an architecture.

    The agentic pipeline:
    1. Analysis Agent — infers scalability and complexity from requirements
    2. Planning Agent — recommends an architecture pattern based on inferred factors
    """
    # Create agent context for greenfield mode
    context = AgentContext(
        mode="greenfield",
        requirements=req,
    )

    # Run the agent pipeline
    orchestrator = Orchestrator()
    result = await orchestrator.run(context)

    # Build response
    return GreenfieldResponse(
        analysis=GreenfieldAnalysis(
            scalability=result.inferred_scalability or "medium",
            complexity=result.inferred_complexity or "medium",
        ),
        suggestion=result.suggestion or {
            "suggested_architecture": "Unknown",
            "reason": "Analysis could not determine a recommendation.",
        },
        agent_logs=result.agent_logs,
    )
