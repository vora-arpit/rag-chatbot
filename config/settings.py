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

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# PDF
PDF_PATH = os.getenv("PDF_PATH", "f:/RAG/Arpit J. Vora.pdf")

# RAG constants
COLLECTION_NAME = "rag_docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "models/gemini-embedding-001"
# LLM_MODEL = os.getenv("LLM_MODEL", "models/gemini-2.5-flash")
VECTOR_SIZE = 3072
TOP_K = 3