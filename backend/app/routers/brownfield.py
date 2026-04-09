"""
Brownfield router: POST /brownfield
Accepts a ZIP file upload of an existing codebase and returns
architecture analysis via the agentic pipeline.
"""
import os
import shutil
import tempfile
import zipfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import (
    BrownfieldResponse, BrownfieldAnalysis, MetricsResult,
    GraphData, ArchitectureSuggestion,
)
from app.agents.base import AgentContext
from app.agents.orchestrator import Orchestrator

router = APIRouter()


@router.post("/brownfield", response_model=BrownfieldResponse)
async def analyze_brownfield(file: UploadFile = File(...)):
    """
    Analyze an existing codebase (uploaded as ZIP) and suggest an architecture.

    The agentic pipeline:
    1. Analysis Agent — parses code, builds dependency graph, computes metrics
    2. Planning Agent — recommends an architecture pattern based on metrics
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are accepted. Please upload a .zip file."
        )

    # Create temp directory and extract ZIP
    temp_dir = tempfile.mkdtemp(prefix="archplanner_")
    try:
        # Save uploaded file
        zip_path = os.path.join(temp_dir, "upload.zip")
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)

        # Extract ZIP
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid ZIP file. The uploaded file could not be extracted."
            )

        # If ZIP contains a single top-level directory, use that
        contents = os.listdir(extract_dir)
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            project_dir = os.path.join(extract_dir, contents[0])
        else:
            project_dir = extract_dir

        # Create agent context for brownfield mode
        context = AgentContext(
            mode="brownfield",
            code_path=project_dir,
        )

        # Run the agent pipeline
        orchestrator = Orchestrator()
        result = await orchestrator.run(context)

        # Build response
        metrics = result.metrics or {
            "avg_instability": 0.0,
            "dependency_density": 0.0,
            "total_modules": 0,
            "risk_score": 0.0,
        }

        # Build per-module list from context (AnalysisAgent populates this)
        from app.models import ModuleMetrics
        per_module_list = [
            ModuleMetrics(
                module=pm.get("module", "unknown"),
                fan_in=pm.get("fan_in", 0),
                fan_out=pm.get("fan_out", 0),
                instability=pm.get("instability", 0.0),
            )
            for pm in (result.per_module_metrics or [])
        ]

        return BrownfieldResponse(
            analysis=BrownfieldAnalysis(
                metrics=MetricsResult(
                    avg_instability=metrics.get("avg_instability", 0.0),
                    dependency_density=metrics.get("dependency_density", 0.0),
                    total_modules=metrics.get("total_modules", 0),
                    risk_score=metrics.get("risk_score", 0.0),
                    per_module=per_module_list,
                ),
                risk_score=result.risk_score or 0.0,
            ),
            suggestion=ArchitectureSuggestion(**(result.suggestion or {
                "suggested_architecture": "Unknown",
                "reason": "Analysis could not determine a recommendation.",
            })),
            graph=GraphData(**(result.graph_data or {"nodes": [], "edges": []})),
            agent_logs=result.agent_logs,
        )

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
