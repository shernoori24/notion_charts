# Run backend (PowerShell helper)
# Usage: .\run-backend.ps1

# Activate venv (assumes venv is in project root)
& .\venv\Scripts\Activate.ps1

# Run from project root:
python -m uvicorn backend.app:app --reload --port 8000

# Alternative: if you are inside the backend/ directory run:
# python -m uvicorn app:app --reload --port 8000
