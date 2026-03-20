"""
Code Analysis Agent (Brownfield)
Takes existing code and returns issue detection with refactoring recommendations.
"""

from langchain_community.chat_models import ChatOllama
from agents.state import AgentState

# Setup LLM (FREE — Ollama local)
llm = ChatOllama(model="llama3")

def code_agent(state: AgentState) -> AgentState:
    """
    Brownfield Agent — takes existing code or a code description
    and returns issue detection with refactoring recommendations.
    """
    print("\n🔵 [Code Analysis Agent] Reviewing existing code...")

    prompt = f"""
You are a software architecture reviewer.

Analyze the following system:

--- AST STRUCTURAL GRAPH (Dependencies & Classes) ---
{state.get('ast_summary', 'No structural graph available.')}

--- RAW CODE / DESCRIPTION ---
{state['input']}

Do the following:
1. Identify architectural issues based heavily on the AST dependency graph (circular dependencies, tight coupling across files, etc.).
2. Detect poor modularization or bad separation of concerns.
3. Suggest concrete improvements referencing specific classes or imports from the graph.
4. Recommend a better architecture if needed.
5. Prioritize issues by severity: High / Medium / Low.

Keep answer structured and actionable.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Code Analysis Agent] Analysis complete.")
    return {"analysis_report": response.content}
