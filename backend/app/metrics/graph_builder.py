"""
Graph builder: constructs a NetworkX DiGraph from dependency edges
and serializes it for frontend visualization (React Flow).
"""
from __future__ import annotations
from typing import List, Tuple, Dict, Any
import networkx as nx


def build_graph(dependencies: List[Tuple[str, str]]) -> nx.DiGraph:
    """
    Build a directed dependency graph.
    Nodes are module names, edges represent 'imports' relationship.
    Edge (A, B) means A depends on (imports) B.
    """
    DG = nx.DiGraph()

    for source, target in dependencies:
        DG.add_edge(source, target)

    return DG


def serialize_graph(graph: nx.DiGraph) -> Dict[str, Any]:
    """
    Serialize a NetworkX DiGraph into a format suitable for React Flow.
    Returns: {nodes: [{id, label, ...}], edges: [{id, source, target}]}
    """
    nodes = []
    for i, node in enumerate(graph.nodes()):
        # Position nodes in a grid layout (frontend will re-layout with dagre)
        fan_in = graph.in_degree(node)
        fan_out = graph.out_degree(node)
        instability = fan_out / (fan_in + fan_out) if (fan_in + fan_out) > 0 else 0

        nodes.append({
            "id": node,
            "label": _short_name(node),
            "fan_in": fan_in,
            "fan_out": fan_out,
            "instability": round(instability, 3),
        })

    edges = []
    for i, (source, target) in enumerate(graph.edges()):
        edges.append({
            "id": f"e-{source}-{target}",
            "source": source,
            "target": target,
        })

    return {"nodes": nodes, "edges": edges}


def _short_name(module_path: str) -> str:
    """Get a short display name from a module path."""
    parts = module_path.replace("\\", "/").split("/")
    return parts[-1] if parts else module_path
