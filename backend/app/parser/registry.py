"""
Parser registry: detects language by file extension and dispatches
to the appropriate parser. Returns a list of (source, target) dependency edges.
"""
from __future__ import annotations
import os
from typing import List, Tuple

from .python_parser import parse_python_imports
from .javascript_parser import parse_javascript_imports
from .java_parser import parse_java_imports


# Extension → parser function mapping
PARSERS = {
    ".py": parse_python_imports,
    ".js": parse_javascript_imports,
    ".jsx": parse_javascript_imports,
    ".ts": parse_javascript_imports,
    ".tsx": parse_javascript_imports,
    ".mjs": parse_javascript_imports,
    ".java": parse_java_imports,
}

# Extensions to skip entirely
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".cache",
    "target", ".idea", ".vscode", ".gradle",
}

SKIP_FILES = {
    "__init__.py", "setup.py", "conftest.py",
}


def detect_language(filepath: str) -> str | None:
    """Detect language from file extension."""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext in (".py",):
        return "python"
    elif ext in (".js", ".jsx", ".ts", ".tsx", ".mjs"):
        return "javascript"
    elif ext in (".java",):
        return "java"
    return None


def parse_project(project_path: str) -> List[Tuple[str, str]]:
    """
    Walk a project directory, parse all supported files, and return
    a list of (source_module, imported_module) dependency edges.
    """
    all_dependencies: List[Tuple[str, str]] = []

    for root, dirs, files in os.walk(project_path):
        # Filter out directories we want to skip
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if filename in SKIP_FILES:
                continue

            filepath = os.path.join(root, filename)
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            parser_fn = PARSERS.get(ext)
            if parser_fn is None:
                continue

            # Get relative path as module name
            rel_path = os.path.relpath(filepath, project_path)
            # Normalize to forward slashes and remove extension
            module_name = rel_path.replace("\\", "/")
            module_name = os.path.splitext(module_name)[0]

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    source_code = f.read()

                imports = parser_fn(source_code, module_name)
                for imported in imports:
                    all_dependencies.append((module_name, imported))
            except Exception:
                # Skip files that can't be read
                continue

    return all_dependencies
