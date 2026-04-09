"""
Analysis Agent — "The Doctor"
Understands and diagnoses the system:
  - Greenfield: extracts scalability/complexity from requirements text
  - Brownfield: parses code, builds dependency graph, computes metrics
"""
from __future__ import annotations
import re
from .base import BaseAgent, AgentContext


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent that acts as a software analyst.
    It tells us WHAT the system looks like.

    Real-world analogy: A doctor diagnosing a patient before treatment.
    """

    name = "AnalysisAgent"
    description = "Analyzes project requirements or existing codebase to produce metrics and insights"

    async def run(self, context: AgentContext) -> AgentContext:
        if context.mode == "greenfield":
            return await self._analyze_greenfield(context)
        elif context.mode == "brownfield":
            return await self._analyze_brownfield(context)
        else:
            context.errors.append(f"Unknown mode: {context.mode}")
            return context

    # ── Greenfield Analysis ─────────────────────────────────────

    async def _analyze_greenfield(self, context: AgentContext) -> AgentContext:
        """Analyze project requirements text to infer scalability and complexity."""
        self.log(context, "Starting greenfield analysis")

        req = context.requirements
        if req is None:
            context.errors.append("No requirements provided for greenfield analysis")
            return context

        description = req.description.lower() if hasattr(req, 'description') else ""
        explicit_scalability = getattr(req, 'scalability', 'medium') or 'medium'
        explicit_complexity = getattr(req, 'complexity', 'medium') or 'medium'
        explicit_users = getattr(req, 'expected_users', 'medium') or 'medium'

        # Infer scalability from description keywords
        scalability = self._infer_scalability(description, explicit_scalability, explicit_users)
        self.log(context, f"Inferred scalability: {scalability}")

        # Infer complexity from description keywords
        complexity = self._infer_complexity(description, explicit_complexity)
        self.log(context, f"Inferred complexity: {complexity}")

        context.inferred_scalability = scalability
        context.inferred_complexity = complexity

        self.log(context, "Greenfield analysis complete")
        return context

    def _infer_scalability(self, desc: str, explicit: str, users: str) -> str:
        """Infer scalability from description text and explicit fields."""
        high_keywords = [
            "microservices", "scale", "scalable", "high availability",
            "distributed", "millions", "100k", "real-time", "streaming",
            "global", "multi-region", "load balancing", "horizontal scaling",
            "elastic", "cloud-native", "kubernetes", "k8s",
        ]
        low_keywords = [
            "simple", "prototype", "mvp", "proof of concept", "poc",
            "internal tool", "small team", "personal", "hobby",
            "single user", "local", "basic",
        ]

        high_score = sum(1 for kw in high_keywords if kw in desc)
        low_score = sum(1 for kw in low_keywords if kw in desc)

        # Check for explicit user count numbers
        user_numbers = re.findall(r'(\d+[kKmM]?)\s*users?', desc)
        for num_str in user_numbers:
            num = self._parse_number(num_str)
            if num >= 100_000:
                high_score += 3
            elif num >= 10_000:
                high_score += 1
            elif num < 100:
                low_score += 1

        # Combine with explicit input
        if explicit == "high" or users == "high":
            high_score += 2
        elif explicit == "low" or users == "low":
            low_score += 2

        if high_score > low_score + 1:
            return "high"
        elif low_score > high_score + 1:
            return "low"
        return "medium"

    def _infer_complexity(self, desc: str, explicit: str) -> str:
        """Infer complexity from description text and explicit field."""
        high_keywords = [
            "complex", "enterprise", "multi-tenant", "microservices",
            "event-driven", "cqrs", "saga", "workflow", "orchestration",
            "machine learning", "ai", "real-time", "streaming",
            "authentication", "authorization", "rbac", "multi-language",
            "legacy", "migration", "integration",
        ]
        low_keywords = [
            "simple", "basic", "crud", "todo", "landing page",
            "static", "blog", "portfolio", "single page",
            "prototype", "mvp",
        ]

        high_score = sum(1 for kw in high_keywords if kw in desc)
        low_score = sum(1 for kw in low_keywords if kw in desc)

        if explicit == "high":
            high_score += 2
        elif explicit == "low":
            low_score += 2

        if high_score > low_score + 1:
            return "high"
        elif low_score > high_score + 1:
            return "low"
        return "medium"

    @staticmethod
    def _parse_number(s: str) -> int:
        """Parse number strings like '100k', '1M', '5000'."""
        s = s.strip().upper()
        if s.endswith('K'):
            return int(float(s[:-1]) * 1_000)
        elif s.endswith('M'):
            return int(float(s[:-1]) * 1_000_000)
        try:
            return int(s)
        except ValueError:
            return 0

    # ── Brownfield Analysis ─────────────────────────────────────

    async def _analyze_brownfield(self, context: AgentContext) -> AgentContext:
        """Parse codebase, build dependency graph, compute metrics."""
        self.log(context, "Starting brownfield analysis")

        if context.code_path is None:
            context.errors.append("No code path provided for brownfield analysis")
            return context

        # Step 1: Parse code to extract dependencies
        self.log(context, "Step 1: Parsing codebase for import dependencies")
        from app.parser.registry import parse_project
        dependencies = parse_project(context.code_path)
        context.dependencies = dependencies
        self.log(context, f"Found {len(dependencies)} dependency edges")

        # Step 2: Build dependency graph
        self.log(context, "Step 2: Building dependency graph")
        from app.metrics.graph_builder import build_graph, serialize_graph
        graph = build_graph(dependencies)
        context.graph_data = serialize_graph(graph)
        self.log(context, f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # Step 3: Compute metrics
        self.log(context, "Step 3: Computing architecture metrics")
        from app.metrics.calculator import compute_metrics
        metrics_result = compute_metrics(graph)
        context.metrics = metrics_result["metrics"]
        context.risk_score = metrics_result["risk_score"]
        context.per_module_metrics = metrics_result.get("per_module", [])
        self.log(context, f"Risk score: {context.risk_score:.2f}")

        self.log(context, "Brownfield analysis complete")
        return context
