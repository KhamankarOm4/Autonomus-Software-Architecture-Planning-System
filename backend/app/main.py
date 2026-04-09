"""
FastAPI application entry point.
Mounts CORS middleware and includes greenfield/brownfield routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import greenfield, brownfield

app = FastAPI(
    title="Web Architecture Planner",
    description=(
        "AI-driven tool that plans and evolves web application architecture. "
        "Supports Greenfield (start-up planning) and Brownfield (existing code analysis) modes."
    ),
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(greenfield.router, tags=["Greenfield"])
app.include_router(brownfield.router, tags=["Brownfield"])


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Web Architecture Planner",
        "version": "1.0.0",
        "endpoints": [
            {"method": "POST", "path": "/greenfield", "description": "Analyze project requirements"},
            {"method": "POST", "path": "/brownfield", "description": "Analyze existing codebase ZIP"},
        ],
    }
