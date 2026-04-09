"""
Tests for language parsers: Python, JavaScript, Java.
Verifies that each parser correctly extracts import dependencies.
"""
import os
import pytest

from app.parser.python_parser import parse_python_imports
from app.parser.javascript_parser import parse_javascript_imports
from app.parser.java_parser import parse_java_imports
from app.parser.registry import parse_project, detect_language


# ── Python Parser Tests ──────────────────────────────────────────

class TestPythonParser:
    """Test Python import extraction."""

    def test_import_statement(self):
        source = "import os\nimport sys\n"
        result = parse_python_imports(source)
        assert "os" in result
        assert "sys" in result

    def test_from_import(self):
        source = "from flask import Flask\nfrom os.path import join\n"
        result = parse_python_imports(source)
        assert "flask" in result
        assert "os.path" in result

    def test_import_as(self):
        source = "import numpy as np\nimport pandas as pd\n"
        result = parse_python_imports(source)
        assert "numpy" in result
        assert "pandas" in result

    def test_dotted_import(self):
        source = "import app.models\nfrom app.utils import helper\n"
        result = parse_python_imports(source)
        assert "app.models" in result
        assert "app.utils" in result

    def test_empty_source(self):
        result = parse_python_imports("")
        assert result == []

    def test_no_imports(self):
        source = "x = 1\nprint(x)\n"
        result = parse_python_imports(source)
        assert result == []


# ── JavaScript Parser Tests ──────────────────────────────────────

class TestJavaScriptParser:
    """Test JavaScript/TypeScript import extraction."""

    def test_es6_import(self):
        source = "import React from 'react'\nimport { useState } from 'react'\n"
        result = parse_javascript_imports(source)
        assert "react" in result

    def test_require(self):
        source = "const express = require('express')\nconst path = require('path')\n"
        result = parse_javascript_imports(source)
        assert "express" in result
        assert "path" in result

    def test_relative_import(self):
        source = "import App from './App'\nimport utils from '../utils/helper'\n"
        result = parse_javascript_imports(source)
        assert "./App" in result
        assert "../utils/helper" in result

    def test_export_from(self):
        source = "export { default } from './Component'\n"
        result = parse_javascript_imports(source)
        assert "./Component" in result

    def test_side_effect_import(self):
        source = "import './styles.css'\n"
        result = parse_javascript_imports(source)
        assert "./styles.css" in result

    def test_empty_source(self):
        result = parse_javascript_imports("")
        assert result == []


# ── Java Parser Tests ────────────────────────────────────────────

class TestJavaParser:
    """Test Java import extraction."""

    def test_import_statement(self):
        source = "import java.util.List;\nimport java.util.Map;\n"
        result = parse_java_imports(source)
        assert "java.util.List" in result
        assert "java.util.Map" in result

    def test_static_import(self):
        source = "import static org.junit.Assert.assertEquals;\n"
        result = parse_java_imports(source)
        assert "org.junit.Assert.assertEquals" in result

    def test_wildcard_import(self):
        source = "import java.util.*;\n"
        result = parse_java_imports(source)
        # Wildcard imports should be captured as java.util.*
        assert len(result) >= 1

    def test_empty_source(self):
        result = parse_java_imports("")
        assert result == []


# ── Language Detection Tests ─────────────────────────────────────

class TestLanguageDetection:
    """Test file extension → language detection."""

    def test_python_detection(self):
        assert detect_language("app.py") == "python"

    def test_javascript_detection(self):
        assert detect_language("app.js") == "javascript"
        assert detect_language("app.jsx") == "javascript"
        assert detect_language("app.ts") == "javascript"
        assert detect_language("app.tsx") == "javascript"
        assert detect_language("app.mjs") == "javascript"

    def test_java_detection(self):
        assert detect_language("Main.java") == "java"

    def test_unknown_extension(self):
        assert detect_language("README.md") is None
        assert detect_language("style.css") is None
        assert detect_language("data.json") is None


# ── Project-Level Parser Tests ───────────────────────────────────

class TestProjectParser:
    """Test full project parsing on synthetic sample."""

    SAMPLES_DIR = os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, "samples", "synthetic_project"
    )

    def test_parse_synthetic_project(self):
        path = os.path.abspath(self.SAMPLES_DIR)
        if not os.path.isdir(path):
            pytest.skip("Synthetic project not found")

        deps = parse_project(path)
        assert isinstance(deps, list)
        assert len(deps) > 0

        # Each dependency is a (source, target) tuple
        for src, tgt in deps:
            assert isinstance(src, str)
            assert isinstance(tgt, str)

    def test_parse_empty_dir(self, tmp_path):
        deps = parse_project(str(tmp_path))
        assert deps == []

    def test_skips_pycache(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-311.py").write_text("import os")
        deps = parse_project(str(tmp_path))
        assert deps == []
