# PowerShell helper to create venv, install deps, and run the FastAPI app
if (-not (Test-Path -Path ".venv")) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
