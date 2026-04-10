"""
AST Parser Utility
Extracts classes, functions, and imports from Python AND JavaScript/TypeScript files.
"""

import ast
import os
import re
from typing import Dict, List


def parse_python_file(filepath: str) -> Dict:
    """Parses a single Python file and returns its structural elements."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except Exception as e:
        return {"error": str(e)}

    imports = []
    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imports.append(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)
            if bases:
                classes.append(f"{node.name} (Inherits: {', '.join(bases)})")
            else:
                classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "raw_classes": [
            {
                "name": node.name,
                "bases": [
                    (base.id if isinstance(base, ast.Name) else base.attr)
                    for base in node.bases
                    if isinstance(base, (ast.Name, ast.Attribute))
                ]
            }
            for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
    }


def parse_js_ts_file(filepath: str) -> Dict:
    """
    Parses a JS/TS/JSX/TSX file using regex to extract:
    - ES6 classes
    - React function components (exported functions / arrow functions)
    - Interfaces and type aliases
    - Import statements
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}

    classes = []
    functions = []
    imports = []

    # ES6 classes: class Foo extends Bar
    for m in re.finditer(r'\bclass\s+(\w+)(?:\s+extends\s+(\w+))?', content):
        name, parent = m.group(1), m.group(2)
        if parent:
            classes.append(f"{name} (Inherits: {parent})")
        else:
            classes.append(name)

    # TS interfaces: interface Foo
    for m in re.finditer(r'\binterface\s+(\w+)', content):
        classes.append(f"{m.group(1)} (Interface)")

    # Exported function components (named exports):
    # export function Foo(  /  export default function Foo(  /  export const Foo = (
    for m in re.finditer(
        r'export\s+(?:default\s+)?(?:function|const|async function)\s+([A-Z]\w*)',
        content
    ):
        name = m.group(1)
        if name not in classes:
            functions.append(name)

    # Arrow component assigned to const (UpperCase → React component)
    for m in re.finditer(r'const\s+([A-Z]\w*)\s*=\s*(?:async\s*)?\(', content):
        name = m.group(1)
        if name not in classes and name not in functions:
            functions.append(name)

    # Import statements: import X from 'y'  /  import { A, B } from 'z'
    for m in re.finditer(r"from\s+['\"]([^'\"]+)['\"]", content):
        imports.append(m.group(1))

    return {
        "imports": imports[:10],
        "classes": classes,
        "functions": functions[:15],
    }


def generate_ast_summary(path: str) -> str:
    """
    Crawls a directory (or single file), parses Python AND JS/TS files,
    and returns a formatted structural summary of the codebase.
    """
    if not os.path.exists(path):
        return "Path does not exist."

    PYTHON_EXTS = {".py"}
    JS_EXTS = {".js", ".jsx", ".ts", ".tsx"}
    # Skip these dirs for JS projects (huge, irrelevant)
    SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build",
                 "__pycache__", ".venv", "venv", ".mypy_cache"}

    summary_lines = ["=== CODEBASE ARCHITECTURE & DEPENDENCY GRAPH ==="]

    def should_skip(root: str) -> bool:
        parts = set(root.replace("\\", "/").split("/"))
        return bool(parts & SKIP_DIRS) or any(p.startswith('.') for p in parts)

    def process_file(filepath: str, relpath: str):
        ext = os.path.splitext(filepath)[1].lower()
        if ext in PYTHON_EXTS:
            data = parse_python_file(filepath)
        elif ext in JS_EXTS:
            data = parse_js_ts_file(filepath)
        else:
            return
        if "error" in data:
            return
        summary_lines.append(f"\n[FILE] {relpath}")
        _format_file_data(data, summary_lines)

    if os.path.isfile(path):
        process_file(path, os.path.basename(path))
    elif os.path.isdir(path):
        # Skip unhelpful/noisy paths like shadcn UI boilerplate (substring check)
        skip_path_substrings = ["components/ui", "components\\ui", ".next", "node_modules", "dist", "build"]

        for root, dirs, files in os.walk(path):
            if should_skip(root) or any(skip in root for skip in skip_path_substrings):
                dirs.clear()
                continue

            # Prune skipped subdirs in-place so os.walk won't descend
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            for file in sorted(files):
                ext = os.path.splitext(file)[1].lower()
                if ext in PYTHON_EXTS | JS_EXTS:
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, path)
                    process_file(filepath, relpath)

    if len(summary_lines) == 1:
        summary_lines.append("\nNo Python/JS/TS AST structure extracted.")

    return "\n".join(summary_lines)


def _format_file_data(data: Dict, summary_lines: List[str]):
    """Helper to format parsed data into text lines."""
    if data.get("imports"):
        summary_lines.append(f"  Imports: {', '.join(data['imports'][:10])}{'...' if len(data['imports']) > 10 else ''}")
    if data.get("classes"):
        summary_lines.append(f"  Classes: {', '.join(data['classes'])}")
    if data.get("functions"):
        summary_lines.append(f"  Functions: {', '.join(data['functions'][:15])}{'...' if len(data['functions']) > 15 else ''}")
