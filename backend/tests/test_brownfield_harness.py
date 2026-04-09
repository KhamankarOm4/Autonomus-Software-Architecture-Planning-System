"""
Brownfield test harness: iterates over all ZIP files in /samples/,
POSTs each to /brownfield, validates the response schema, and
outputs a CSV summary of results.

Usage:
    cd backend
    python -m pytest tests/test_brownfield_harness.py -v -s
"""
import os
import csv
import io
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

SAMPLES_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "samples"
)

RESULTS_CSV = os.path.join(
    os.path.dirname(__file__), "brownfield_results.csv"
)

VALID_ARCHITECTURES = {
    "Hexagonal Architecture",
    "Layered Architecture",
    "Microservices",
    "MVC",
    "Modular Monolith",
}


def _find_zip_files():
    """Find all .zip files in the samples directory."""
    if not os.path.isdir(SAMPLES_DIR):
        return []
    return [
        f for f in os.listdir(SAMPLES_DIR)
        if f.lower().endswith(".zip")
    ]


def _validate_response(data: dict) -> list[str]:
    """Validate the response schema. Returns list of error messages."""
    errors = []

    if "analysis" not in data:
        errors.append("Missing 'analysis' field")
    else:
        analysis = data["analysis"]
        if "metrics" not in analysis:
            errors.append("Missing 'analysis.metrics' field")
        else:
            metrics = analysis["metrics"]
            for field in ("avg_instability", "dependency_density", "total_modules", "risk_score"):
                if field not in metrics:
                    errors.append(f"Missing 'analysis.metrics.{field}'")

    if "suggestion" not in data:
        errors.append("Missing 'suggestion' field")
    else:
        suggestion = data["suggestion"]
        if "suggested_architecture" not in suggestion:
            errors.append("Missing 'suggestion.suggested_architecture'")
        elif suggestion["suggested_architecture"] not in VALID_ARCHITECTURES:
            errors.append(f"Unknown architecture: {suggestion['suggested_architecture']}")
        if "reason" not in suggestion:
            errors.append("Missing 'suggestion.reason'")

    if "graph" not in data:
        errors.append("Missing 'graph' field")

    if "agent_logs" not in data:
        errors.append("Missing 'agent_logs' field")

    return errors


class TestBrownfieldHarness:
    """Batch test all sample ZIP files against the brownfield endpoint."""

    @pytest.fixture(autouse=True)
    def _setup_results(self):
        """Initialize results collection."""
        self.results = []
        yield
        # Write CSV after all tests
        if self.results:
            self._write_csv()

    def _write_csv(self):
        """Write results to CSV."""
        with open(RESULTS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "filename", "status", "architecture", "risk_score",
                "modules", "instability", "density", "errors",
            ])
            writer.writeheader()
            writer.writerows(self.results)

    def _record_result(self, filename, status, data=None, errors=None):
        """Record one result."""
        row = {
            "filename": filename,
            "status": status,
            "architecture": "",
            "risk_score": "",
            "modules": "",
            "instability": "",
            "density": "",
            "errors": "; ".join(errors or []),
        }
        if data:
            suggestion = data.get("suggestion", {})
            metrics = data.get("analysis", {}).get("metrics", {})
            row["architecture"] = suggestion.get("suggested_architecture", "")
            row["risk_score"] = metrics.get("risk_score", "")
            row["modules"] = metrics.get("total_modules", "")
            row["instability"] = metrics.get("avg_instability", "")
            row["density"] = metrics.get("dependency_density", "")
        self.results.append(row)

    def test_all_sample_zips(self):
        """POST each sample ZIP to /brownfield and validate response."""
        zip_files = _find_zip_files()

        if not zip_files:
            pytest.skip("No ZIP files found in samples/")

        for zip_name in zip_files:
            zip_path = os.path.join(SAMPLES_DIR, zip_name)

            with open(zip_path, "rb") as f:
                response = client.post(
                    "/brownfield",
                    files={"file": (zip_name, f, "application/zip")},
                )

            if response.status_code != 200:
                self._record_result(
                    zip_name, "HTTP_ERROR",
                    errors=[f"HTTP {response.status_code}: {response.text[:200]}"]
                )
                continue

            data = response.json()
            schema_errors = _validate_response(data)

            if schema_errors:
                self._record_result(zip_name, "SCHEMA_ERROR", data, schema_errors)
            else:
                self._record_result(zip_name, "OK", data)

        # Assert at least one passed
        ok_count = sum(1 for r in self.results if r["status"] == "OK")
        assert ok_count > 0, f"No samples passed validation. Results: {self.results}"
