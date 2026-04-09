"""
Tests for FastAPI endpoints: POST /greenfield, POST /brownfield, GET /.
Uses FastAPI TestClient with httpx for synchronous testing.
"""
import os
import io
import zipfile
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

SAMPLES_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "samples"
)


# ── Health Check ─────────────────────────────────────────────────

class TestHealthCheck:
    """Test GET / health endpoint."""

    def test_health_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_health_response_shape(self):
        response = client.get("/")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "endpoints" in data


# ── Greenfield Endpoint ──────────────────────────────────────────

class TestGreenfieldEndpoint:
    """Test POST /greenfield endpoint."""

    def test_valid_request(self):
        payload = {
            "description": "A web application for managing tasks with user authentication and real-time updates",
            "expected_users": "medium",
            "scalability": "medium",
            "complexity": "medium",
            "constraints": [],
        }
        response = client.post("/greenfield", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "analysis" in data
        assert "suggestion" in data
        assert "agent_logs" in data

    def test_response_analysis_shape(self):
        payload = {
            "description": "A simple CRUD application for internal team use",
        }
        response = client.post("/greenfield", json=payload)
        data = response.json()

        assert "scalability" in data["analysis"]
        assert "complexity" in data["analysis"]
        assert data["analysis"]["scalability"] in ("low", "medium", "high")
        assert data["analysis"]["complexity"] in ("low", "medium", "high")

    def test_response_suggestion_shape(self):
        payload = {
            "description": "An enterprise distributed microservices platform for millions of users",
            "scalability": "high",
            "complexity": "high",
        }
        response = client.post("/greenfield", json=payload)
        data = response.json()

        suggestion = data["suggestion"]
        assert "suggested_architecture" in suggestion
        assert "reason" in suggestion
        assert len(suggestion["reason"]) > 0

    def test_short_description_rejected(self):
        payload = {"description": "short"}
        response = client.post("/greenfield", json=payload)
        assert response.status_code == 422  # validation error

    def test_missing_description_rejected(self):
        payload = {"scalability": "high"}
        response = client.post("/greenfield", json=payload)
        assert response.status_code == 422

    def test_agent_logs_present(self):
        payload = {
            "description": "A web application for managing inventory with barcode scanning",
        }
        response = client.post("/greenfield", json=payload)
        data = response.json()

        logs = data["agent_logs"]
        assert isinstance(logs, list)
        assert len(logs) > 0
        # Check log structure
        assert "agent" in logs[0]
        assert "message" in logs[0]
        assert "timestamp" in logs[0]


# ── Brownfield Endpoint ──────────────────────────────────────────

def _create_test_zip(files: dict) -> io.BytesIO:
    """Create an in-memory ZIP with given filename → content mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    buf.seek(0)
    return buf


class TestBrownfieldEndpoint:
    """Test POST /brownfield endpoint."""

    def test_valid_zip_upload(self):
        zip_buf = _create_test_zip({
            "project/app.py": "from models import User\nfrom views import render\n",
            "project/models.py": "from database import connect\n",
            "project/views.py": "from models import User\nfrom utils import format_date\n",
            "project/utils.py": "import os\nimport json\n",
            "project/database.py": "import sqlite3\n",
        })

        response = client.post(
            "/brownfield",
            files={"file": ("test_project.zip", zip_buf, "application/zip")},
        )
        assert response.status_code == 200

        data = response.json()
        assert "analysis" in data
        assert "suggestion" in data
        assert "graph" in data
        assert "agent_logs" in data

    def test_response_metrics_shape(self):
        zip_buf = _create_test_zip({
            "app.py": "from models import User\n",
            "models.py": "import os\n",
        })

        response = client.post(
            "/brownfield",
            files={"file": ("test.zip", zip_buf, "application/zip")},
        )
        data = response.json()

        metrics = data["analysis"]["metrics"]
        assert "avg_instability" in metrics
        assert "dependency_density" in metrics
        assert "total_modules" in metrics
        assert "risk_score" in metrics

    def test_response_graph_shape(self):
        zip_buf = _create_test_zip({
            "app.py": "from models import User\n",
            "models.py": "import os\n",
        })

        response = client.post(
            "/brownfield",
            files={"file": ("test.zip", zip_buf, "application/zip")},
        )
        data = response.json()

        graph = data["graph"]
        assert "nodes" in graph
        assert "edges" in graph

    def test_non_zip_rejected(self):
        buf = io.BytesIO(b"this is not a zip file")
        response = client.post(
            "/brownfield",
            files={"file": ("test.txt", buf, "text/plain")},
        )
        assert response.status_code == 400

    def test_invalid_zip_rejected(self):
        buf = io.BytesIO(b"PK\x03\x04corrupted data here")
        response = client.post(
            "/brownfield",
            files={"file": ("bad.zip", buf, "application/zip")},
        )
        assert response.status_code == 400

    def test_no_file_rejected(self):
        response = client.post("/brownfield")
        assert response.status_code == 422

    def test_sample_zip_upload(self):
        """Test with the bundled synthetic_project.zip if available."""
        zip_path = os.path.join(SAMPLES_DIR, "synthetic_project.zip")
        if not os.path.exists(zip_path):
            pytest.skip("synthetic_project.zip not found")

        with open(zip_path, "rb") as f:
            response = client.post(
                "/brownfield",
                files={"file": ("synthetic_project.zip", f, "application/zip")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["suggestion"]["suggested_architecture"] in [
            "Hexagonal Architecture",
            "Layered Architecture",
            "Microservices",
            "MVC",
            "Modular Monolith",
        ]
