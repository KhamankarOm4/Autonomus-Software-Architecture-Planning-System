"""
Architecture Agent (Greenfield)
Takes requirements for a NEW system and returns an architecture plan.
"""

from langchain_community.chat_models import ChatOllama
from agents.state import AgentState

# Setup LLM (FREE — Ollama local)
llm = ChatOllama(model="llama3")

def architecture_agent(state: AgentState) -> AgentState:
    """
    Architecture Agent — takes requirements (Greenfield) 
    OR an existing code analysis report (Brownfield) 
    and returns a system architecture plan.
    """
    if state["mode"] == "greenfield":
        print("\n🟢 [Architecture Agent] Designing from scratch (Greenfield)...")
        context = f"Requirements:\n{state['input']}"
    else:
        print("\n🟢 [Architecture Agent] Designing refactored architecture (Brownfield)...")
        context = f"Existing Codebase Analysis Report:\n{state['analysis_report']}\n\nExisting AST Structure:\n{state.get('ast_summary', '')}"

    prompt = f"""
You are an expert software architect.

Based on the following context, build or refactor the architecture.

{context}

--- PAST ARCHITECTURAL KNOWLEDGE (RAG Memory) ---
{state.get('past_memory', 'No past memory found.')}
-------------------------------------------------

Do the following:
1. Suggest best architecture (Microservices, MVC, Layered, Event-Driven, etc.). Align with PAST ARCHITECTURAL KNOWLEDGE if relevant.
2. Suggest design patterns (Factory, Observer, Strategy, etc.)
3. Provide modular decomposition with key components and their responsibilities
4. Explain your reasoning clearly

Keep answer structured and concise.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Architecture Agent] Plan generated.")
    return {"architecture_plan": response.content}
