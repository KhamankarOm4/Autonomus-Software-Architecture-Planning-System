"""
Python import parser using Tree-sitter with regex fallback.
Extracts import dependencies from Python source code.
"""
from __future__ import annotations
import re
from typing import List

# Try to use tree-sitter; fall back to regex if unavailable
_USE_TREE_SITTER = False
_ts_parser = None
_ts_language = None

try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser

    PY_LANGUAGE = Language(tspython.language())
    _ts_parser = Parser(PY_LANGUAGE)
    _USE_TREE_SITTER = True
except Exception:
    pass


def parse_python_imports(source: str, module_name: str = "") -> List[str]:
    """
    Extract import targets from Python source code.
    Returns a list of imported module names.
    """
    if _USE_TREE_SITTER and _ts_parser is not None:
        return _parse_with_tree_sitter(source)
    return _parse_with_regex(source)


def _parse_with_tree_sitter(source: str) -> List[str]:
    """Parse Python imports using tree-sitter AST."""
    tree = _ts_parser.parse(bytes(source, "utf-8"))
    root = tree.root_node
    imports = []

    for node in _walk(root):
        if node.type == "import_statement":
            # import foo, import foo.bar
            for child in node.children:
                if child.type == "dotted_name":
                    imports.append(child.text.decode("utf-8"))
                elif child.type == "aliased_import":
                    for sub in child.children:
                        if sub.type == "dotted_name":
                            imports.append(sub.text.decode("utf-8"))
                            break

        elif node.type == "import_from_statement":
            # from foo import bar
            module_node = None
            for child in node.children:
                if child.type == "dotted_name":
                    module_node = child.text.decode("utf-8")
                    break
                elif child.type == "relative_import":
                    module_node = child.text.decode("utf-8")
                    break
            if module_node:
                imports.append(module_node)

    return imports


def _walk(node):
    """Walk all nodes in a tree-sitter AST."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _parse_with_regex(source: str) -> List[str]:
    """Fallback: parse Python imports using regex."""
    imports = []

    for line in source.splitlines():
        line = line.strip()

        # import foo / import foo.bar / import foo as f
        match = re.match(r'^import\s+([\w.]+)', line)
        if match:
            imports.append(match.group(1))
            continue

        # from foo import bar / from foo.bar import baz
        match = re.match(r'^from\s+([\w.]+)\s+import', line)
        if match:
            imports.append(match.group(1))
            continue

    return imports
