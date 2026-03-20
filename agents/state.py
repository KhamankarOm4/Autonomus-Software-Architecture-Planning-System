"""
Shared state definition for the LangGraph multi-agent system.
"""

from typing import TypedDict

class AgentState(TypedDict):
    input: str          # User's requirements or code snippet
    mode: str           # "greenfield" or "brownfield"
    ast_summary: str    # Parsed structural graph of the codebase
    output: str         # Final agent response
