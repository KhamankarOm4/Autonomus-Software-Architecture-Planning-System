"""
JavaScript/TypeScript import parser using Tree-sitter with regex fallback.
Extracts import/require dependencies from JS/TS/JSX/TSX source code.
"""
from __future__ import annotations
import re
from typing import List

# Try to use tree-sitter; fall back to regex if unavailable
_USE_TREE_SITTER = False
_ts_parser = None

try:
    import tree_sitter_javascript as tsjs
    from tree_sitter import Language, Parser

    JS_LANGUAGE = Language(tsjs.language())
    _ts_parser = Parser(JS_LANGUAGE)
    _USE_TREE_SITTER = True
except Exception:
    pass


def parse_javascript_imports(source: str, module_name: str = "") -> List[str]:
    """
    Extract import targets from JavaScript/TypeScript source code.
    Returns a list of imported module/path names.
    """
    if _USE_TREE_SITTER and _ts_parser is not None:
        return _parse_with_tree_sitter(source)
    return _parse_with_regex(source)


def _parse_with_tree_sitter(source: str) -> List[str]:
    """Parse JS imports using tree-sitter AST."""
    tree = _ts_parser.parse(bytes(source, "utf-8"))
    root = tree.root_node
    imports = []

    for node in _walk(root):
        # import ... from 'module'
        if node.type == "import_statement":
            source_node = node.child_by_field_name("source")
            if source_node and source_node.type == "string":
                val = source_node.text.decode("utf-8").strip("'\"")
                imports.append(val)

        # const x = require('module')
        elif node.type == "call_expression":
            func = node.child_by_field_name("function")
            if func and func.text == b"require":
                args = node.child_by_field_name("arguments")
                if args and args.child_count > 0:
                    for child in args.children:
                        if child.type == "string":
                            val = child.text.decode("utf-8").strip("'\"")
                            imports.append(val)
                            break

        # export ... from 'module'
        elif node.type == "export_statement":
            source_node = node.child_by_field_name("source")
            if source_node and source_node.type == "string":
                val = source_node.text.decode("utf-8").strip("'\"")
                imports.append(val)

    return imports


def _walk(node):
    """Walk all nodes in a tree-sitter AST."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _parse_with_regex(source: str) -> List[str]:
    """Fallback: parse JS/TS imports using regex."""
    imports = []

    for line in source.splitlines():
        line = line.strip()

        # import ... from 'module' / import ... from "module"
        match = re.search(r'''from\s+['"]([^'"]+)['"]''', line)
        if match:
            imports.append(match.group(1))
            continue

        # require('module') / require("module")
        match = re.search(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)''', line)
        if match:
            imports.append(match.group(1))
            continue

        # import 'module' (side-effect import)
        match = re.match(r'''^\s*import\s+['"]([^'"]+)['"]''', line)
        if match:
            imports.append(match.group(1))
            continue

        # export ... from 'module'
        match = re.search(r'''export\s+.*from\s+['"]([^'"]+)['"]''', line)
        if match:
            imports.append(match.group(1))
            continue

    return imports
