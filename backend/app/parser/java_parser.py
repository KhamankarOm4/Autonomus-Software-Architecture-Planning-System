"""
Java import parser using Tree-sitter with regex fallback.
Extracts import and package dependencies from Java source code.
"""
from __future__ import annotations
import re
from typing import List

# Try to use tree-sitter; fall back to regex if unavailable
_USE_TREE_SITTER = False
_ts_parser = None

try:
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser

    JAVA_LANGUAGE = Language(tsjava.language())
    _ts_parser = Parser(JAVA_LANGUAGE)
    _USE_TREE_SITTER = True
except Exception:
    pass


def parse_java_imports(source: str, module_name: str = "") -> List[str]:
    """
    Extract import targets from Java source code.
    Returns a list of imported package/class names.
    """
    if _USE_TREE_SITTER and _ts_parser is not None:
        return _parse_with_tree_sitter(source)
    return _parse_with_regex(source)


def _parse_with_tree_sitter(source: str) -> List[str]:
    """Parse Java imports using tree-sitter AST."""
    tree = _ts_parser.parse(bytes(source, "utf-8"))
    root = tree.root_node
    imports = []

    for node in _walk(root):
        if node.type == "import_declaration":
            # Get the full import path
            for child in node.children:
                if child.type == "scoped_identifier" or child.type == "identifier":
                    import_name = child.text.decode("utf-8")
                    # Get the top-level package (e.g., com.example.foo → com.example.foo)
                    imports.append(import_name)
                    break

    return imports


def _walk(node):
    """Walk all nodes in a tree-sitter AST."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _parse_with_regex(source: str) -> List[str]:
    """Fallback: parse Java imports using regex."""
    imports = []

    for line in source.splitlines():
        line = line.strip()

        # import com.example.Foo;
        # import static com.example.Foo.method;
        match = re.match(r'^import\s+(?:static\s+)?([\w.]+)\s*;', line)
        if match:
            imports.append(match.group(1))
            continue

    return imports
