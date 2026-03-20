"""
======================================================================
 Autonomous Software Architecture Planning System
 Multi-Agent System using LangGraph + Ollama (llama3)
======================================================================
"""

import os
from langgraph.graph import StateGraph

# Import extracted components
from agents.state import AgentState
from agents.greenfield import architecture_agent
from agents.brownfield import code_agent
from agents.router import router
from agents.utils import read_codebase
from agents.ast_parser import generate_ast_summary

# ─────────────────────────────────────────────
# Build and Compile LangGraph
# ─────────────────────────────────────────────
builder = StateGraph(AgentState)

# Register agent nodes
builder.add_node("architecture", architecture_agent)
builder.add_node("code", code_agent)

# Set router as the conditional entry point
builder.set_conditional_entry_point(router)

# Brownfield flows into Greenfield for architecture refactoring
builder.add_edge("code", "architecture")

# Only Architecture Agent is the terminal node now
builder.set_finish_point("architecture")

# Compile the graph
graph = builder.compile()

# ─────────────────────────────────────────────
# Main — Interactive CLI Loop
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

        ast_summary_text = ""

        # ── Get input ──
        if mode == "greenfield":
            user_input = input("Enter your requirements: ").strip()
        else:
            print("\n[Brownfield Mode]")
            print("You can paste code, describe the system, OR provide a file/folder path.")
            user_input = input("Enter code or path: ").strip()

            # Check if the input is actually a valid file or directory path
            if os.path.exists(user_input):
                print(f"📁 Detected path. Extracting AST Structural Graph from: {user_input} ...")
                ast_summary_text = generate_ast_summary(user_input)
                
                print(f"📁 Reading full codebase content...")
                code_content = read_codebase(user_input)
                if code_content.strip():
                    user_input = code_content
                    print(f"✅ AST Parse complete. Loaded {len(code_content)} characters of code.")
                else:
                    print("⚠️  No readable code found in path.")
                    continue

        if not user_input:
            print("⚠️  Input cannot be empty.\n")
            continue

        print("\n⏳ Processing...\n")

        # ── Run the graph ──
        result = graph.invoke({
            "input": user_input,
            "mode": mode,
            "ast_summary": ast_summary_text,
            "analysis_report": "",
            "architecture_plan": ""
        })

        # ── Display result ──
        if mode == "brownfield":
            print("\n" + "=" * 60)
            print("📋 [CODE ANALYSIS REPORT]")
            print("=" * 60)
            print(result.get("analysis_report", "No report generated."))
            
            print("\n" + "=" * 60)
            print("🏗️ [REFACTORED ARCHITECTURE PLAN]")
            print("=" * 60)
            print(result.get("architecture_plan", "No architecture plan generated."))
            print("=" * 60 + "\n")
        else:
            print("\n" + "=" * 60)
            print("🏗️ [ARCHITECTURE PLAN]")
            print("=" * 60)
            print(result.get("architecture_plan", "No architecture plan generated."))
            print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
