"""
Run the FastAPI backend.
Usage: python run_backend.py
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "backend.app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000",
        ],
        check=True,
    )
