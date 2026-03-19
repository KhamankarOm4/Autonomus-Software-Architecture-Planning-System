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
    Greenfield Agent — takes requirements and returns
    an architecture plan, design patterns, and modular breakdown.
    """
    print("\n🟢 [Architecture Agent] Analyzing requirements...")

    prompt = f"""
You are an expert software architect.

Based on the following requirements:
{state['input']}

Do the following:
1. Suggest best architecture (Microservices, MVC, Layered, Event-Driven, etc.)
2. Suggest design patterns (Factory, Observer, Strategy, etc.)
3. Provide modular decomposition with key components and their responsibilities
4. Explain your reasoning clearly

Keep answer structured and concise.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Architecture Agent] Plan generated.")
    return {"output": response.content}
