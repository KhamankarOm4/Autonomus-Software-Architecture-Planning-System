"""
======================================================================
 Autonomous Software Architecture Planning System
 Multi-Agent System using LangGraph + Ollama (llama3)
======================================================================

 AGENTS:
   1. Architecture Agent  (Greenfield) — requirements → architecture plan
   2. Code Analysis Agent (Brownfield) — code → issue detection

 ROUTER:
   set_conditional_entry_point → directs to the correct agent based on mode.

 LLM:
   ChatOllama running locally with llama3 model.

 USAGE:
   python agents.py

 REQUIREMENTS:
   pip install langgraph langchain langchain-community
   ollama pull llama3
======================================================================
"""

# ─────────────────────────────────────────────
# STEP 3: Define State (Core of LangGraph)
# ─────────────────────────────────────────────
from typing import TypedDict

class AgentState(TypedDict):
    input: str          # User's requirements or code snippet
    mode: str           # "greenfield" or "brownfield"
    output: str         # Final agent response


# ─────────────────────────────────────────────
# STEP 4: Setup LLM (FREE — Ollama local)
# ─────────────────────────────────────────────
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3")


# ─────────────────────────────────────────────
# STEP 5: Agent 1 — Architecture Agent
#         (Greenfield: NEW project design)
#
#  Based on the project PDF:
#  → Suggest architecture pattern
#  → Suggest design patterns
#  → Modular decomposition
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# STEP 6: Agent 2 — Code Analysis Agent
#         (Brownfield: EXISTING code review)
#
#  Based on the project PDF:
#  → Detect tight coupling
#  → Detect bad structure / anti-patterns
#  → Suggest improvements
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# STEP 7: Router (Brain of the System)
#
#  Reads the "mode" from AgentState and decides
#  which agent node to activate.
# ─────────────────────────────────────────────
def router(state: AgentState) -> str:
    """
    Routes to 'architecture' (Greenfield) or 'code' (Brownfield)
    based on the 'mode' field in AgentState.
    """
    if state["mode"] == "greenfield":
        print("\n🔀 Router → Architecture Agent (Greenfield)")
        return "architecture"
    else:
        print("\n🔀 Router → Code Analysis Agent (Brownfield)")
        return "code"


# ─────────────────────────────────────────────
# STEP 8: Build and Compile LangGraph
# ─────────────────────────────────────────────
from langgraph.graph import StateGraph

builder = StateGraph(AgentState)

# Register agent nodes
builder.add_node("architecture", architecture_agent)
builder.add_node("code", code_agent)

# Set router as the conditional entry point
builder.set_conditional_entry_point(router)

# Both agents are finish/terminal nodes
builder.set_finish_point("architecture")
builder.set_finish_point("code")

# Compile the graph
graph = builder.compile()


# ─────────────────────────────────────────────
# STEP 9: Main — Interactive CLI Loop
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  🚀 Autonomous Software Architecture Planning System")
    print("       Powered by LangGraph + Ollama (llama3)")
    print("=" * 60)
    print("\n📌 Modes:")
    print("   🟢 greenfield → Design a NEW system from requirements")
    print("   🔵 brownfield → Analyze EXISTING code for issues")
    print("\nType 'exit' to quit.\n")

    while True:
        # ── Get mode ──
        mode = input("Mode (greenfield / brownfield): ").strip().lower()

        if mode in ("exit", "quit", "q"):
            print("\n👋 Goodbye!")
            break

        if mode not in ("greenfield", "brownfield"):
            print("⚠️  Please enter 'greenfield' or 'brownfield'.\n")
            continue

        # ── Get input ──
        if mode == "greenfield":
            user_input = input("Enter your requirements: ").strip()
        else:
            user_input = input("Paste your code or describe the system: ").strip()

        if not user_input:
            print("⚠️  Input cannot be empty.\n")
            continue

        print("\n⏳ Processing...\n")

        # ── Run the graph ──
        result = graph.invoke({
            "input": user_input,
            "mode": mode,
            "output": ""
        })

        # ── Display result ──
        label = "ARCHITECTURE PLAN" if mode == "greenfield" else "CODE ANALYSIS REPORT"
        print("\n" + "=" * 60)
        print(f"📋 [{label}]")
        print("=" * 60)
        print(result["output"])
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
