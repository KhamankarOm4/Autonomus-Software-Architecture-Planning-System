"""
Architecture Agent (Greenfield)
Takes requirements for a NEW system and returns an architecture plan.
"""

from langchain_community.chat_models import ChatOllama
from agents.state import AgentState
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

# Instantly switch to Groq Cloud API if the key exists, otherwise use local Ollama
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)
    print("☁️ [Greenfield] Using lightning-fast Groq Cloud API for Llama-3...")
else:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3")
    print("💻 [Greenfield] Using local Ollama for Llama-3...")

def architecture_agent(state: AgentState) -> AgentState:
    """
    Architecture Agent — takes requirements (Greenfield) 
    OR an existing code analysis report (Brownfield) 
    and returns a system architecture plan.
    """
    if state["mode"] == "greenfield":
        print("\n🟢 [Architecture Agent] Designing from scratch (Greenfield)...")
        context = f"Requirements:\n{state['input']}"
        action_instructions = """1. Suggest best architecture (Microservices, MVC, Layered, Event-Driven, etc.). Align with PAST ARCHITECTURAL KNOWLEDGE if relevant.
2. Provide a HIGHLY DETAILED modular decomposition grouped strictly by Topic/Business Domain.
3. For each Topic/Module, explicitly list the exact Class Names to be built.
4. Detail exactly how those classes Connect to each other and their relation to one another (Inheritance, Composition, or API calls).
5. Suggest design patterns (Factory, Observer, Strategy, etc.) to use for those class relations.
6. Generate a visual Dependency Graph using Mermaid.js (` ```mermaid graph TD ... ``` `) that plots all the classes and their exact connections to each other."""
        class_whitelist_section = ""
    else:
        print("\n🟢 [Architecture Agent] Designing refactored architecture (Brownfield)...")
        ast_summary = state.get('ast_summary', '')
        analysis_report = state.get('analysis_report', '')
        readme = state.get('readme_content', '')
        context = f"Project Requirements/README:\n{readme}\n\nExisting Codebase Analysis Report:\n{analysis_report}\n\nExisting AST Structure:\n{ast_summary}"

        # Extract actual class + component names from AST — covers Python classes,
        # React components, TS interfaces, and exported functions
        import re as _re
        all_classes = []
        seen = set()

        def _add(name):
            name = name.strip()
            if name and name not in seen and len(name) > 1:
                seen.add(name)
                all_classes.append(name)

        for line in ast_summary.splitlines():
            # Classes: Foo (Interface), Bar (Inherits: Baz)
            if line.strip().startswith("Classes:"):
                for cls in line.replace("Classes:", "").split(","):
                    name = _re.sub(r'\s*\(.*?\)', '', cls).strip()
                    _add(name)
            # Functions: HomePage, PostCard, Layout  (React components = UpperCase)
            elif line.strip().startswith("Functions:"):
                for fn in line.replace("Functions:", "").split(","):
                    fn = fn.strip().rstrip("...")
                    if fn and fn[0].isupper():  # Only UpperCase = React component
                        _add(fn)

        class_whitelist_section = f"""
⚠️ STRICT RULE — ACTUAL COMPONENTS & CLASSES FROM CODEBASE:
The following names were extracted directly from the codebase files via AST/regex parsing.
You MUST only use these names in your analysis and Mermaid diagram.
Do NOT rename, invent, or add any component/class not in this list:
{chr(10).join(f'  - {c}' for c in all_classes) if all_classes else '  (No classes detected — use file names from the AST Structure above)'}
"""
        action_instructions = """1. Review the existing AST Structure and Analysis Report.
2. Suggest how to REFACTOR the existing architecture (separating concerns, decoupling, applying patterns).
3. Group the ACTUAL CLASSES listed above into logical bounded contexts or modules.
4. Detail exactly how the refactored classes (from the whitelist only) connect to each other.
5. Generate a visual Dependency Graph using Mermaid.js (` ```mermaid graph TD ... ``` `) using ONLY the actual class names from the whitelist above."""

    prompt = f"""
You are an expert software architect.

Based on the following context, build or refactor the architecture.

{context}

{class_whitelist_section}
--- PAST ARCHITECTURAL KNOWLEDGE (RAG Memory) ---
{state.get('past_memory', 'No past memory found.')}
-------------------------------------------------

Do the following:
{action_instructions}

Keep answer structured, extremely detailed, and concise.
"""

    response = llm.invoke(prompt)
    print("\n✅ [Architecture Agent] Plan generated.")
    return {"architecture_plan": response.content}
