"""
Code Analysis Agent (Brownfield)
Takes existing code and returns issue detection with refactoring recommendations.
"""

from langchain_community.chat_models import ChatOllama
from agents.state import AgentState
import os
from dotenv import load_dotenv

load_dotenv()

# Instantly switch to Groq Cloud API if the key exists, otherwise use local Ollama
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)
    print("☁️ [Brownfield] Using lightning-fast Groq Cloud API for Llama-3...")
else:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3")
    print("💻 [Brownfield] Using local Ollama for Llama-3...")

def code_agent(state: AgentState) -> AgentState:
    """
    Brownfield Agent — takes existing code or a code description
    and returns issue detection with refactoring recommendations.
    """
    print("\n🔵 [Code Analysis Agent] Reviewing existing code...")

    prompt = f"""
You are a software architecture reviewer.

Analyze the following system:

--- PROJECT TOPIC / IDEA (README) ---
{state.get('readme_content', 'No README provided.')}

--- PAST ARCHITECTURAL KNOWLEDGE (Company Standard / RAG) ---
{state.get('past_memory', 'No past memory found.')}

--- AST STRUCTURAL GRAPH (Dependencies & Classes) ---
{state.get('ast_summary', 'No structural graph available.')}

--- RAW CODE / DESCRIPTION ---
{state['input']}

Do the following:
1. Identify architectural issues based heavily on the AST dependency graph (circular dependencies, tight coupling across files, etc.).
2. Detect poor modularization or bad separation of concerns. Check if it violates PAST ARCHITECTURAL KNOWLEDGE.
3. Suggest concrete improvements referencing specific classes or imports from the graph.
4. Recommend a better architecture if needed.
5. Prioritize issues by severity: High / Medium / Low.

Keep answer structured and actionable.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Code Analysis Agent] Analysis complete.")
    return {"analysis_report": response.content}
