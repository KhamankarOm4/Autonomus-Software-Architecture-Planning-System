"""
Tests for the agent pipeline: AnalysisAgent, PlanningAgent, Orchestrator.
Covers both greenfield and brownfield modes end-to-end.
"""
import os
import pytest
import asyncio

# ── Helpers ──────────────────────────────────────────────────────

def run_async(coro):
    """Run an async function synchronously in tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ── Fixtures ─────────────────────────────────────────────────────

SAMPLES_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "samples", "synthetic_project"
)


def _greenfield_context(**overrides):
    """Create a greenfield AgentContext with sensible defaults."""
    from app.agents.base import AgentContext
    from app.models import ProjectRequirements

    req = ProjectRequirements(
        description=overrides.pop("description", "A simple CRUD web application with user authentication"),
        expected_users=overrides.pop("expected_users", "medium"),
        scalability=overrides.pop("scalability", "medium"),
        complexity=overrides.pop("complexity", "medium"),
        constraints=overrides.pop("constraints", []),
    )
    return AgentContext(mode="greenfield", requirements=req, **overrides)


def _brownfield_context():
    """Create a brownfield AgentContext pointing at synthetic project."""
    from app.agents.base import AgentContext

    path = os.path.abspath(SAMPLES_DIR)
    return AgentContext(mode="brownfield", code_path=path)


# ── AnalysisAgent Tests ──────────────────────────────────────────

class TestAnalysisAgentGreenfield:
    """Test AnalysisAgent with greenfield requirements."""

    def test_infer_scalability_high(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _greenfield_context(
            description="A distributed microservices platform for millions of users with real-time streaming",
            scalability="high",
            expected_users="high",
        )
        result = run_async(agent.run(ctx))
        assert result.inferred_scalability == "high"

    def test_infer_scalability_low(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _greenfield_context(
            description="A simple personal hobby project prototype for local use",
            scalability="low",
            expected_users="low",
        )
        result = run_async(agent.run(ctx))
        assert result.inferred_scalability == "low"

    def test_infer_complexity_high(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _greenfield_context(
            description="An enterprise multi-tenant CQRS event-driven system with machine learning",
            complexity="high",
        )
        result = run_async(agent.run(ctx))
        assert result.inferred_complexity == "high"

    def test_infer_complexity_low(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _greenfield_context(
            description="A simple basic todo CRUD app, just a prototype",
            complexity="low",
        )
        result = run_async(agent.run(ctx))
        assert result.inferred_complexity == "low"

    def test_agent_logs_populated(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _greenfield_context()
        result = run_async(agent.run(ctx))
        agent_msgs = [l for l in result.agent_logs if l["agent"] == "AnalysisAgent"]
        assert len(agent_msgs) >= 3  # start + inferred scalability + inferred complexity + complete

    def test_missing_requirements(self):
        from app.agents.base import AgentContext
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = AgentContext(mode="greenfield", requirements=None)
        result = run_async(agent.run(ctx))
        assert len(result.errors) > 0


class TestAnalysisAgentBrownfield:
    """Test AnalysisAgent with brownfield codebase analysis."""

    def test_parses_dependencies(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _brownfield_context()
        result = run_async(agent.run(ctx))
        assert len(result.dependencies) > 0

    def test_builds_graph(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _brownfield_context()
        result = run_async(agent.run(ctx))
        assert result.graph_data is not None
        assert "nodes" in result.graph_data
        assert "edges" in result.graph_data
        assert len(result.graph_data["nodes"]) > 0

    def test_computes_metrics(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _brownfield_context()
        result = run_async(agent.run(ctx))
        assert result.metrics is not None
        assert "avg_instability" in result.metrics
        assert "dependency_density" in result.metrics
        assert "total_modules" in result.metrics

    def test_computes_risk_score(self):
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = _brownfield_context()
        result = run_async(agent.run(ctx))
        assert result.risk_score is not None
        assert 0.0 <= result.risk_score <= 1.0

    def test_missing_code_path(self):
        from app.agents.base import AgentContext
        from app.agents.analysis_agent import AnalysisAgent

        agent = AnalysisAgent()
        ctx = AgentContext(mode="brownfield", code_path=None)
        result = run_async(agent.run(ctx))
        assert len(result.errors) > 0


# ── PlanningAgent Tests ──────────────────────────────────────────

class TestPlanningAgent:
    """Test PlanningAgent decision logic."""

    def test_greenfield_recommendation(self):
        from app.agents.planning_agent import PlanningAgent
        from app.agents.base import AgentContext

        agent = PlanningAgent()
        ctx = AgentContext(mode="greenfield")
        ctx.inferred_scalability = "high"
        ctx.inferred_complexity = "high"
        result = run_async(agent.run(ctx))
        assert result.suggestion is not None
        assert "suggested_architecture" in result.suggestion

    def test_brownfield_high_risk(self):
        from app.agents.planning_agent import PlanningAgent
        from app.agents.base import AgentContext

        agent = PlanningAgent()
        ctx = AgentContext(mode="brownfield")
        ctx.metrics = {
            "avg_instability": 0.9,
            "dependency_density": 0.8,
            "total_modules": 10,
        }
        ctx.risk_score = 0.85
        ctx.per_module_metrics = [{"module": "a", "fan_in": 1, "fan_out": 12}]
        result = run_async(agent.run(ctx))
        assert result.suggestion is not None
        # High instability + high fan-out → should suggest Hexagonal
        assert result.suggestion["suggested_architecture"] == "Hexagonal Architecture"

    def test_brownfield_low_risk(self):
        from app.agents.planning_agent import PlanningAgent
        from app.agents.base import AgentContext

        agent = PlanningAgent()
        ctx = AgentContext(mode="brownfield")
        ctx.metrics = {
            "avg_instability": 0.3,
            "dependency_density": 0.1,
            "total_modules": 5,
        }
        ctx.risk_score = 0.25
        ctx.per_module_metrics = [{"module": "a", "fan_in": 2, "fan_out": 1}]
        result = run_async(agent.run(ctx))
        assert result.suggestion is not None
        assert result.suggestion["suggested_architecture"] == "Modular Monolith"

    def test_suggestion_has_pros_cons(self):
        from app.agents.planning_agent import PlanningAgent
        from app.agents.base import AgentContext

        agent = PlanningAgent()
        ctx = AgentContext(mode="greenfield")
        ctx.inferred_scalability = "medium"
        ctx.inferred_complexity = "medium"
        result = run_async(agent.run(ctx))
        assert "pros" in result.suggestion
        assert "cons" in result.suggestion
        assert len(result.suggestion["pros"]) > 0


# ── Orchestrator Tests ───────────────────────────────────────────

class TestOrchestrator:
    """Test full pipeline end-to-end."""

    def test_greenfield_pipeline(self):
        from app.agents.orchestrator import Orchestrator

        orchestrator = Orchestrator()
        ctx = _greenfield_context(
            description="A high-scale distributed microservices platform for streaming data",
            scalability="high",
            complexity="high",
        )
        result = run_async(orchestrator.run(ctx))

        # Analysis agent should have filled inference
        assert result.inferred_scalability is not None
        assert result.inferred_complexity is not None

        # Planning agent should have made a suggestion
        assert result.suggestion is not None
        assert "suggested_architecture" in result.suggestion

        # Logs should show the full pipeline
        orchestrator_logs = [l for l in result.agent_logs if l["agent"] == "Orchestrator"]
        assert len(orchestrator_logs) >= 2  # started + completed

    def test_brownfield_pipeline(self):
        from app.agents.orchestrator import Orchestrator

        orchestrator = Orchestrator()
        ctx = _brownfield_context()
        result = run_async(orchestrator.run(ctx))

        # Analysis agent should have filled metrics
        assert result.metrics is not None
        assert result.risk_score is not None
        assert result.graph_data is not None
        assert len(result.dependencies) > 0

        # Planning agent should have made a suggestion
        assert result.suggestion is not None
        assert "suggested_architecture" in result.suggestion

    def test_agent_logs_order(self):
        from app.agents.orchestrator import Orchestrator

        orchestrator = Orchestrator()
        ctx = _greenfield_context()
        result = run_async(orchestrator.run(ctx))

        agents_seen = [l["agent"] for l in result.agent_logs]
        # Orchestrator starts, then AnalysisAgent, then PlanningAgent, then Orchestrator ends
        assert agents_seen[0] == "Orchestrator"
        assert "AnalysisAgent" in agents_seen
        assert "PlanningAgent" in agents_seen
        assert agents_seen[-1] == "Orchestrator"
