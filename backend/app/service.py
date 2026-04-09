import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load .env from project root so GROQ_API_KEY etc. are available
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")


def _fallback_greenfield_plan(requirements: str) -> str:
    return (
        "## Proposed Architecture (Fallback)\n\n"
        "- Pattern: Layered + modular monolith (safe default)\n"
        "- Modules: `api`, `application`, `domain`, `infrastructure`\n"
        "- Start with clear boundaries and evolve to microservices only when needed.\n\n"
        "### Inputs\n"
        f"{requirements[:1500]}"
    )


def _fallback_brownfield_report(user_input: str) -> str:
    return (
        "## Brownfield Analysis (Fallback)\n\n"
        "- High: Unknown coupling hotspots (LLM pipeline unavailable).\n"
        "- Medium: Missing architecture conformance checks.\n"
        "- Low: Documentation and ownership boundaries may be unclear.\n\n"
        "Recommendation: enable LangGraph/LangChain runtime and rerun for deep analysis.\n\n"
        "### Input Snapshot\n"
        f"{user_input[:1500]}"
    )


def _imports() -> Dict[str, Any]:
    from langgraph.graph import StateGraph

    from agents.ast_parser import generate_ast_summary
    from agents.brownfield import code_agent
    from agents.graph_builder import parse_ast_summary_to_graph, parse_mermaid_to_graph
    from agents.greenfield import architecture_agent
    from agents.memory import forget_memory, retrieve_memory, train_memory
    from agents.router import router
    from agents.state import AgentState
    from agents.utils import read_codebase

    return {
        "StateGraph": StateGraph,
        "AgentState": AgentState,
        "architecture_agent": architecture_agent,
        "code_agent": code_agent,
        "router": router,
        "read_codebase": read_codebase,
        "generate_ast_summary": generate_ast_summary,
        "parse_ast_summary_to_graph": parse_ast_summary_to_graph,
        "parse_mermaid_to_graph": parse_mermaid_to_graph,
        "train_memory": train_memory,
        "retrieve_memory": retrieve_memory,
        "forget_memory": forget_memory,
    }


def _build_graph(mods: Dict[str, Any]):
    builder = mods["StateGraph"](mods["AgentState"])
    builder.add_node("architecture", mods["architecture_agent"])
    builder.add_node("code", mods["code_agent"])
    builder.set_conditional_entry_point(mods["router"])
    builder.add_edge("code", "architecture")
    builder.set_finish_point("architecture")
    return builder.compile()


def run_analysis(mode: str, user_input: str) -> Dict[str, Any]:
    mode = mode.lower().strip()
    user_input = user_input.strip('\"\'')
    if mode not in {"greenfield", "brownfield"}:
        raise ValueError("mode must be 'greenfield' or 'brownfield'")

    warning = ""
    ast_summary_text = ""
    readme_text = ""
    input_payload = user_input
    graph_data = {"nodes": [], "edges": []}
    memory_used = "No past architectural memory found."

    try:
        mods = _imports()
        graph = _build_graph(mods)
    except Exception as exc:
        warning = f"Agent runtime unavailable: {exc}"
        if mode == "greenfield":
            return {
                "mode": mode,
                "analysis_report": "",
                "architecture_plan": _fallback_greenfield_plan(user_input),
                "ast_summary": "",
                "graph": graph_data,
                "memory_used": memory_used,
                "warning": warning,
            }
        return {
            "mode": mode,
            "analysis_report": _fallback_brownfield_report(user_input),
            "architecture_plan": _fallback_greenfield_plan("Refactor existing system with bounded contexts."),
            "ast_summary": "",
            "graph": graph_data,
            "memory_used": memory_used,
            "warning": warning,
        }
    if mode == "greenfield" and os.path.exists(user_input) and os.path.isfile(user_input):
        extracted = mods["extract_document_text"](user_input)
        if not extracted.startswith("Error"):
            input_payload = extracted

    if mode == "brownfield" and os.path.exists(user_input):
        readme_path = os.path.join(user_input, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as rf:
                readme_text = rf.read()

        ast_summary_text = mods["generate_ast_summary"](user_input)
        input_payload = mods["read_codebase"](user_input) or user_input
        graph_data = mods["parse_ast_summary_to_graph"](ast_summary_text)

    search_query = input_payload if mode == "greenfield" else (ast_summary_text[:4000] or "Software architecture refactoring")
    try:
        memory_used = mods["retrieve_memory"](search_query)
    except Exception as exc:
        warning = f"Memory lookup failed: {exc}"

    result = graph.invoke(
        {
            "input": input_payload,
            "mode": mode,
            "readme_content": readme_text,
            "past_memory": memory_used,
            "ast_summary": ast_summary_text,
            "analysis_report": "",
            "architecture_plan": "",
        }
    )

    architecture_plan = result.get("architecture_plan", "") or ""
    analysis_report = result.get("analysis_report", "") or ""

    # In both modes, build graph from LLM's proposed Mermaid plan. Note that for Brownfield, 
    # the prompt ensures it only uses real extracted components.
    if architecture_plan:
        graph_data = mods["parse_mermaid_to_graph"](architecture_plan)

    # Normalise graph_data so it always matches GraphPayload schema
    graph_data = {
        "nodes": graph_data.get("nodes", []),
        "edges": graph_data.get("edges", []),
    }

    return {
        "mode": mode,
        "analysis_report": analysis_report,
        "architecture_plan": architecture_plan,
        "ast_summary": ast_summary_text,
        "graph": graph_data,
        "memory_used": memory_used,
        "warning": warning,
    }


def train_memory_from_path(path: str) -> Tuple[bool, str]:
    try:
        mods = _imports()
        mods["train_memory"](path)
        return True, "Training completed."
    except Exception as exc:
        return False, f"Training failed: {exc}"


def forget_memory_by_path(path: str) -> Tuple[bool, str]:
    try:
        mods = _imports()
        mods["forget_memory"](path)
        return True, "Memory deletion completed."
    except Exception as exc:
        return False, f"Memory deletion failed: {exc}"

