"""
Architecture Suggestion Engine.
Applies decision rules to recommend an architecture pattern
based on metrics (brownfield) or inferred requirements (greenfield).

Patterns: Hexagonal, Layered, Microservices, MVC, Modular Monolith
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List


# ── Architecture Pattern Catalog ────────────────────────────────

PATTERNS = {
    "Hexagonal Architecture": {
        "description": (
            "Hexagonal Architecture (Ports & Adapters) isolates core business logic "
            "from external I/O (databases, APIs, UI). The core domain defines ports "
            "(interfaces), and adapters implement them. This makes business logic "
            "testable in isolation and protects it from infrastructure changes."
        ),
        "pros": [
            "Core logic fully testable without infrastructure",
            "Easy to swap databases, APIs, or UI frameworks",
            "Clear separation of concerns",
            "Protects against vendor lock-in",
        ],
        "cons": [
            "Higher initial complexity",
            "More boilerplate (ports + adapters)",
            "Steeper learning curve for teams",
        ],
    },
    "Layered Architecture": {
        "description": (
            "Layered Architecture separates concerns into horizontal layers: "
            "Presentation → Business Logic → Data Access → Database. Each layer "
            "only depends on the layer directly below it, reducing coupling and "
            "making the system easier to understand and maintain."
        ),
        "pros": [
            "Simple and well-understood pattern",
            "Clear separation of concerns",
            "Easy to test each layer independently",
            "Good for small-to-medium applications",
        ],
        "cons": [
            "Can lead to 'layer bloat' in large systems",
            "Strict layering can cause unnecessary indirection",
            "Not ideal for highly distributed systems",
        ],
    },
    "Microservices": {
        "description": (
            "Microservices architecture decomposes the application into small, "
            "independently deployable services, each owning its data and business logic. "
            "Services communicate via APIs (REST, gRPC, messaging). This enables "
            "independent scaling, deployment, and technology choices per service."
        ),
        "pros": [
            "Independent deployment and scaling per service",
            "Technology freedom per service",
            "Fault isolation — one service failure doesn't crash all",
            "Better for large teams (service ownership)",
        ],
        "cons": [
            "Distributed system complexity (network, consistency)",
            "Operational overhead (monitoring, deployment pipelines)",
            "Data consistency challenges (eventual consistency)",
            "Not suitable for small projects or small teams",
        ],
    },
    "MVC": {
        "description": (
            "Model-View-Controller separates the application into three components: "
            "Model (data/business logic), View (UI/presentation), and Controller "
            "(handles input, orchestrates Model and View). Widely used in web "
            "frameworks like Django, Rails, Spring MVC, and Express."
        ),
        "pros": [
            "Widely understood and supported by frameworks",
            "Good separation for typical web applications",
            "Easy onboarding for developers",
            "Well-suited for CRUD-heavy applications",
        ],
        "cons": [
            "Controllers can become 'fat' with complex logic",
            "Not ideal for complex domain logic",
            "Tight coupling between View and Model in some implementations",
        ],
    },
    "Modular Monolith": {
        "description": (
            "A Modular Monolith is a single deployable unit internally organized "
            "into well-defined modules with clear boundaries. Each module has its "
            "own domain logic and data, communicating through well-defined interfaces. "
            "It combines the simplicity of a monolith with the modularity of microservices."
        ),
        "pros": [
            "Simple deployment (single artifact)",
            "Strong module boundaries reduce coupling",
            "Easier refactoring than microservices",
            "Good stepping stone toward microservices if needed",
        ],
        "cons": [
            "Requires discipline to maintain module boundaries",
            "Scaling is all-or-nothing (entire monolith)",
            "Risk of boundary erosion over time",
        ],
    },
}


def suggest_architecture(
    mode: str,
    # Brownfield parameters
    avg_instability: float = 0.5,
    dependency_density: float = 0.5,
    total_modules: int = 0,
    risk_score: float = 0.5,
    per_module: Optional[List[Dict]] = None,
    # Greenfield parameters
    scalability: Optional[str] = None,
    complexity: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Suggest an architecture pattern based on analysis results.

    Returns dict with:
        - suggested_architecture: str
        - reason: str
        - pattern_description: str
        - pros: list[str]
        - cons: list[str]
    """
    if mode == "brownfield":
        return _suggest_brownfield(
            avg_instability, dependency_density, total_modules,
            risk_score, per_module or []
        )
    elif mode == "greenfield":
        return _suggest_greenfield(scalability or "medium", complexity or "medium")
    else:
        return _make_suggestion(
            "MVC",
            "Default recommendation for unknown analysis mode."
        )


def _suggest_brownfield(
    avg_instability: float,
    dependency_density: float,
    total_modules: int,
    risk_score: float,
    per_module: List[Dict],
) -> Dict[str, Any]:
    """Apply brownfield decision rules based on metrics."""

    # Calculate max fan-out from per-module data
    max_fan_out = max((m.get("fan_out", 0) for m in per_module), default=0)

    # Rule 1: Very high instability or fan-out → Hexagonal
    if avg_instability > 0.8 or max_fan_out > 10:
        return _make_suggestion(
            "Hexagonal Architecture",
            f"High instability ({avg_instability:.2f}) and/or high fan-out "
            f"(max {max_fan_out}) indicate that modules are heavily dependent on "
            f"external concerns. Hexagonal Architecture isolates core business "
            f"logic from external I/O, making it testable in isolation and "
            f"reducing fragile dependencies."
        )

    # Rule 2: High risk score → Layered
    if risk_score > 0.7:
        return _make_suggestion(
            "Layered Architecture",
            f"High coupling and dependency density (risk score: {risk_score:.2f}) "
            f"indicate poor modularity and maintainability. A Layered Architecture "
            f"enforces separation of concerns through horizontal layers, reducing "
            f"tight coupling and making the system easier to maintain."
        )

    # Rule 3: Low risk + many modules + high scalability → Microservices
    if risk_score < 0.5 and total_modules > 15:
        return _make_suggestion(
            "Microservices",
            f"Low coupling risk ({risk_score:.2f}) with many modules "
            f"({total_modules}) suggests good modularity. The codebase is "
            f"well-structured enough to decompose into independent microservices "
            f"for better scalability and independent deployment."
        )

    # Rule 4: Moderate risk → MVC
    if 0.4 <= risk_score <= 0.7:
        return _make_suggestion(
            "MVC",
            f"Moderate coupling risk ({risk_score:.2f}) is typical of standard "
            f"web applications. MVC provides a clean separation between data, "
            f"presentation, and control flow that suits this complexity level."
        )

    # Rule 5: Low risk, few modules → Modular Monolith
    return _make_suggestion(
        "Modular Monolith",
        f"Low complexity (risk score: {risk_score:.2f}, {total_modules} modules) "
        f"indicates a well-structured codebase. A Modular Monolith maintains "
        f"simplicity while enforcing clear module boundaries, and can evolve "
        f"toward microservices if scaling needs increase."
    )


def _suggest_greenfield(scalability: str, complexity: str) -> Dict[str, Any]:
    """Apply greenfield decision rules based on inferred requirements."""

    # High scalability + high complexity → Microservices
    if scalability == "high" and complexity in ("high", "medium"):
        return _make_suggestion(
            "Microservices",
            "High expected user load and scalability needs combined with "
            "significant complexity favor a Microservices architecture. "
            "Independent services can scale horizontally and be deployed "
            "and maintained by separate teams."
        )

    # High complexity but lower scalability → Hexagonal
    if complexity == "high" and scalability != "high":
        return _make_suggestion(
            "Hexagonal Architecture",
            "High complexity with moderate scalability needs benefits from "
            "Hexagonal Architecture. It isolates complex business logic from "
            "infrastructure concerns, making the core domain testable and "
            "maintainable as complexity grows."
        )

    # Medium scalability + medium complexity → Layered or MVC
    if scalability == "medium" and complexity == "medium":
        return _make_suggestion(
            "Layered Architecture",
            "Medium scalability and complexity indicate a typical web application. "
            "Layered Architecture provides clean separation of concerns with "
            "Presentation, Business Logic, and Data Access layers — a proven "
            "pattern for this scale."
        )

    # High scalability but low complexity → MVC
    if scalability == "high" and complexity == "low":
        return _make_suggestion(
            "MVC",
            "High scalability with low complexity suggests a straightforward "
            "application that needs to handle significant load. MVC provides "
            "clean structure while keeping the architecture simple enough "
            "to optimize for performance."
        )

    # Low everything → Modular Monolith
    return _make_suggestion(
        "Modular Monolith",
        "Low-to-moderate requirements suggest starting with a Modular Monolith. "
        "It combines deployment simplicity with good internal structure, and "
        "can evolve toward microservices as the project grows."
    )


def _make_suggestion(architecture: str, reason: str) -> Dict[str, Any]:
    """Build a complete suggestion dict with pattern catalog info."""
    pattern = PATTERNS.get(architecture, {})
    return {
        "suggested_architecture": architecture,
        "reason": reason,
        "pattern_description": pattern.get("description", ""),
        "pros": pattern.get("pros", []),
        "cons": pattern.get("cons", []),
    }
