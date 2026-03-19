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

Analyze the following code:
{state['input']}

Do the following:
1. Identify architectural issues (tight coupling, low cohesion, God Object, Spaghetti Code, etc.)
2. Detect poor modularization or bad separation of concerns
3. Suggest concrete improvements with examples
4. Recommend a better architecture if needed
5. Prioritize issues by severity: High / Medium / Low

Keep answer structured and actionable.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Code Analysis Agent] Analysis complete.")
    return {"output": response.content}
