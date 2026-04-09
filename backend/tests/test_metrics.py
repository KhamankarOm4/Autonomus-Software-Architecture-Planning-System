"""
Tests for metrics module: graph builder and metrics calculator.
Uses known graph topologies to verify instability, density, and risk calculations.
"""
import pytest
import networkx as nx

from app.metrics.graph_builder import build_graph, serialize_graph
from app.metrics.calculator import compute_metrics, get_max_fan_out, get_max_fan_in


# ── Graph Builder Tests ──────────────────────────────────────────

class TestGraphBuilder:
    """Test dependency graph construction."""

    def test_build_empty_graph(self):
        graph = build_graph([])
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_build_simple_graph(self):
        deps = [("a", "b"), ("b", "c")]
        graph = build_graph(deps)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 2
        assert graph.has_edge("a", "b")
        assert graph.has_edge("b", "c")

    def test_build_graph_no_duplicates(self):
        deps = [("a", "b"), ("a", "b"), ("b", "c")]
        graph = build_graph(deps)
        assert graph.number_of_edges() == 2  # no duplicate edges in DiGraph

    def test_serialize_graph_structure(self):
        deps = [("app", "models"), ("app", "views"), ("views", "models")]
        graph = build_graph(deps)
        serialized = serialize_graph(graph)

        assert "nodes" in serialized
        assert "edges" in serialized
        assert len(serialized["nodes"]) == 3
        assert len(serialized["edges"]) == 3

    def test_serialized_node_fields(self):
        deps = [("app", "models")]
        graph = build_graph(deps)
        serialized = serialize_graph(graph)

        node = serialized["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "fan_in" in node
        assert "fan_out" in node
        assert "instability" in node

    def test_serialized_edge_fields(self):
        deps = [("app", "models")]
        graph = build_graph(deps)
        serialized = serialize_graph(graph)

        edge = serialized["edges"][0]
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert edge["source"] == "app"
        assert edge["target"] == "models"


# ── Calculator Tests ─────────────────────────────────────────────

class TestMetricsCalculator:
    """Test metrics computation with known graph topologies."""

    def test_empty_graph(self):
        graph = nx.DiGraph()
        result = compute_metrics(graph)

        assert result["metrics"]["avg_instability"] == 0.0
        assert result["metrics"]["dependency_density"] == 0.0
        assert result["metrics"]["total_modules"] == 0
        assert result["risk_score"] == 0.0

    def test_single_node(self):
        graph = nx.DiGraph()
        graph.add_node("a")
        result = compute_metrics(graph)

        assert result["metrics"]["total_modules"] == 1
        assert result["metrics"]["avg_instability"] == 0.0
        assert result["metrics"]["dependency_density"] == 0.0

    def test_linear_chain(self):
        """A → B → C: instability varies by position."""
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "b"), ("b", "c")])
        result = compute_metrics(graph)

        assert result["metrics"]["total_modules"] == 3
        per_mod = {m["module"]: m for m in result["per_module"]}

        # a: fan_in=0, fan_out=1 → instability = 1.0
        assert per_mod["a"]["fan_out"] == 1
        assert per_mod["a"]["fan_in"] == 0
        assert per_mod["a"]["instability"] == 1.0

        # c: fan_in=1, fan_out=0 → instability = 0.0
        assert per_mod["c"]["fan_in"] == 1
        assert per_mod["c"]["fan_out"] == 0
        assert per_mod["c"]["instability"] == 0.0

    def test_star_topology(self):
        """Hub depends on many: hub → a, hub → b, hub → c."""
        graph = nx.DiGraph()
        graph.add_edges_from([("hub", "a"), ("hub", "b"), ("hub", "c")])
        result = compute_metrics(graph)

        per_mod = {m["module"]: m for m in result["per_module"]}

        # hub: fan_in=0, fan_out=3 → instability = 1.0
        assert per_mod["hub"]["instability"] == 1.0
        # a: fan_in=1, fan_out=0 → instability = 0.0
        assert per_mod["a"]["instability"] == 0.0

    def test_density_calculation(self):
        """
        3 nodes, 2 edges: density = 2 / (3 * 2) = 0.3333
        """
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "b"), ("b", "c")])
        result = compute_metrics(graph)

        expected_density = 2 / (3 * 2)
        assert abs(result["metrics"]["dependency_density"] - expected_density) < 0.01

    def test_fully_connected(self):
        """
        3 nodes, all connected: density = 6 / 6 = 1.0
        """
        graph = nx.DiGraph()
        graph.add_edges_from([
            ("a", "b"), ("a", "c"),
            ("b", "a"), ("b", "c"),
            ("c", "a"), ("c", "b"),
        ])
        result = compute_metrics(graph)
        assert result["metrics"]["dependency_density"] == 1.0

    def test_risk_score_formula(self):
        """Risk = 0.7 * avg_instability + 0.3 * density."""
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "b"), ("b", "c")])
        result = compute_metrics(graph)

        avg_inst = result["metrics"]["avg_instability"]
        density = result["metrics"]["dependency_density"]
        expected_risk = 0.7 * avg_inst + 0.3 * density
        assert abs(result["risk_score"] - round(expected_risk, 4)) < 0.01

    def test_risk_score_bounded(self):
        """Risk score stays in [0, 1]."""
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
        result = compute_metrics(graph)
        assert 0.0 <= result["risk_score"] <= 1.0


# ── Helper Function Tests ────────────────────────────────────────

class TestHelperFunctions:
    """Test max fan-in/fan-out helpers."""

    def test_max_fan_out(self):
        graph = nx.DiGraph()
        graph.add_edges_from([("hub", "a"), ("hub", "b"), ("hub", "c"), ("a", "b")])
        assert get_max_fan_out(graph) == 3  # hub has 3 outgoing

    def test_max_fan_in(self):
        graph = nx.DiGraph()
        graph.add_edges_from([("a", "hub"), ("b", "hub"), ("c", "hub")])
        assert get_max_fan_in(graph) == 3  # hub has 3 incoming

    def test_max_fan_out_empty(self):
        assert get_max_fan_out(nx.DiGraph()) == 0

    def test_max_fan_in_empty(self):
        assert get_max_fan_in(nx.DiGraph()) == 0
