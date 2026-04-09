"""
Metrics calculator: computes coupling, instability, density, and risk
from a NetworkX directed dependency graph.

References:
- Instability = fan_out / (fan_in + fan_out)  [Clean Architecture]
- Density = m / (n * (n-1))  [NetworkX directed graph density]
- Risk = 0.7 * avg_instability + 0.3 * dependency_density
"""
from __future__ import annotations
from typing import Dict, Any, List
import networkx as nx


def compute_metrics(graph: nx.DiGraph) -> Dict[str, Any]:
    """
    Compute architecture metrics from the dependency graph.

    Returns dict with:
        - metrics: {avg_instability, dependency_density, total_modules, risk_score}
        - risk_score: float (0.0 - 1.0)
        - per_module: list of per-module metric dicts
    """
    n = graph.number_of_nodes()
    m = graph.number_of_edges()

    if n == 0:
        return {
            "metrics": {
                "avg_instability": 0.0,
                "dependency_density": 0.0,
                "total_modules": 0,
                "risk_score": 0.0,
            },
            "risk_score": 0.0,
            "per_module": [],
        }

    # ── Per-module metrics ──────────────────────────────────
    per_module: List[Dict[str, Any]] = []
    instabilities: List[float] = []

    for node in graph.nodes():
        fan_in = graph.in_degree(node)
        fan_out = graph.out_degree(node)

        if fan_in + fan_out > 0:
            instability = fan_out / (fan_in + fan_out)
        else:
            instability = 0.0

        instabilities.append(instability)
        per_module.append({
            "module": node,
            "fan_in": fan_in,
            "fan_out": fan_out,
            "instability": round(instability, 4),
        })

    # ── Aggregate metrics ───────────────────────────────────

    # Average instability across all modules
    avg_instability = sum(instabilities) / len(instabilities) if instabilities else 0.0

    # Dependency density: m / (n * (n-1)) for directed graphs
    # This matches NetworkX's density formula for directed graphs
    if n > 1:
        dependency_density = m / (n * (n - 1))
    else:
        dependency_density = 0.0

    # Clamp density to [0, 1]
    dependency_density = min(dependency_density, 1.0)

    # Risk score: weighted combination
    risk_score = 0.7 * avg_instability + 0.3 * dependency_density
    risk_score = min(risk_score, 1.0)

    return {
        "metrics": {
            "avg_instability": round(avg_instability, 4),
            "dependency_density": round(dependency_density, 4),
            "total_modules": n,
            "risk_score": round(risk_score, 4),
        },
        "risk_score": round(risk_score, 4),
        "per_module": per_module,
    }


def get_max_fan_out(graph: nx.DiGraph) -> int:
    """Get the maximum fan-out (efferent coupling) in the graph."""
    if graph.number_of_nodes() == 0:
        return 0
    return max(graph.out_degree(n) for n in graph.nodes())


def get_max_fan_in(graph: nx.DiGraph) -> int:
    """Get the maximum fan-in (afferent coupling) in the graph."""
    if graph.number_of_nodes() == 0:
        return 0
    return max(graph.in_degree(n) for n in graph.nodes())
