from pathlib import Path
import os

# Try to load a .env file if python-dotenv is available.
try:
    from dotenv import load_dotenv

    dotenv_path = Path(".") / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()
except Exception:
    dotenv_path = Path(".") / ".env"
    if dotenv_path.exists():
        try:
            for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and val:
                    os.environ.setdefault(key, val)
        except Exception:
            pass

# Export commonly used settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
PDF_PATH = os.getenv("PDF_PATH", "f:/RAG/Arpit J. Vora.pdf")

