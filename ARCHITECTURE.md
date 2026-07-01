# Recommended Project Structure (High-level)

This file proposes a clean, minimal re-organization and provides high-level example code for each layer. I will not change runtime behavior — this is a non-destructive plan and example code you can adopt incrementally.

Goal
- Keep current working code as-is.
- Provide a clear package layout for maintainability and testing.
- Show high-level code for each layer (API, services, config, persistence).

Suggested tree

```
RAG/
├─ .env.example
├─ .env
├─ README.md
├─ requirements.txt
├─ run_dev.ps1
├─ run_dev.sh
├─ ARCHITECTURE.md
├─ src/
│  ├─ __init__.py
│  ├─ main.py                # FastAPI app (entrypoint)
│  ├─ config.py              # config loader (wraps current config/settings.py)
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ routes.py           # routers for upload / match / health
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ ingest_service.py   # PDF reading, chunking, embeddings, qdrant upsert
│  │  ├─ search_service.py   # embed queries, query qdrant, assemble context
│  │  ├─ match_service.py    # resume ↔ jd matching + groq wrapper
│  ├─ clients/
│  │  ├─ __init__.py
│  │  ├─ gemini_client.py    # wraps genai client and retries/backoff
│  │  ├─ qdrant_client.py    # wrapper around qdrant-client usage
│  ├─ web/
│  │  ├─ static/             # frontend assets (index.html, css, js)
│  │  └─ templates/
└─ legacy/                    # keep existing top-level scripts until migrated
   ├─ app.py
   ├─ ingest.py
   ├─ query.py
   ├─ matcher.py
   └─ ...
```

Notes
- Create `src/` gradually and keep `legacy/` until migration is complete. This avoids breaking the running app.
- Use small wrappers in `src/clients` that import and call the existing code in the top-level modules; then refactor the implementation into `src/services` when ready.

High-level code examples

1) Entrypoint: `src/main.py`

```python
from fastapi import FastAPI
from src.api.routes import router as api_router
from src.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title="RAG Resume Matcher")
    app.include_router(api_router, prefix="")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
```

2) Config wrapper: `src/config.py`

```python
from typing import Final
from pathlib import Path
import os
# Optionally import the existing config/settings to keep behavior identical
from config import settings as legacy_settings

# Expose a small set of config constants used by the app
GEMINI_API_KEY: Final = os.getenv("GEMINI_API_KEY") or legacy_settings.GEMINI_API_KEY
QDRANT_URL: Final = os.getenv("QDRANT_URL") or legacy_settings.QDRANT_URL
QDRANT_API_KEY: Final = os.getenv("QDRANT_API_KEY") or legacy_settings.QDRANT_API_KEY
LLM_MODEL: Final = os.getenv("LLM_MODEL", legacy_settings.LLM_MODEL)
EMBEDDING_MODEL: Final = os.getenv("EMBEDDING_MODEL", legacy_settings.EMBEDDING_MODEL)
TOP_K: Final = int(os.getenv("TOP_K", legacy_settings.TOP_K))
```

3) API routes: `src/api/routes.py`

```python
from fastapi import APIRouter, UploadFile, File, Form
from src.services.ingest_service import ingest_resume_file
from src.services.ingest_service import ingest_jd_text
from src.services.match_service import run_match

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok"}

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    num_chunks = await ingest_resume_file(file)
    return {"message": f"Resume ingested, {num_chunks} chunks"}

@router.post("/upload-jd")
async def upload_jd(jd_text: str = Form(...)):
    ingest_jd_text(jd_text)
    return {"message": "Job description ingested"}

@router.post("/match")
async def match():
    report = run_match()
    return {"report": report}
```

4) Service layer example: `src/services/ingest_service.py`

```python
from fastapi import UploadFile
import tempfile, os
from legacy import ingest as legacy_ingest

async def ingest_resume_file(file: UploadFile) -> int:
    # write to disk then call legacy ingestion code
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        text = legacy_ingest.read_pdf(tmp_path)
        chunks = legacy_ingest.chunk_text(text)
        legacy_ingest.create_collection()
        legacy_ingest.store_chunks(chunks)
        return len(chunks)
    finally:
        os.unlink(tmp_path)

def ingest_jd_text(jd_text: str):
    # forward to existing ingest_jd implementation
    from legacy import ingest_jd as legacy_jd
    legacy_jd.ingest_jd(jd_text)
```

5) Client wrapper: `src/clients/gemini_client.py`

```python
import time
from google import genai
from src.config import GEMINI_API_KEY
from google.genai.errors import ClientError

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_with_retry(model: str, contents, max_retries=4):
    delay = 1.0
    for _ in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=contents)
        except ClientError as e:
            # if rate limit, wait and backoff
            if getattr(e, "status_code", None) == 429:
                time.sleep(delay)
                delay *= 2
                continue
            raise
```

Migration strategy
- Add `src/` and `legacy/` directories without deleting top-level scripts.
- Gradually implement new modules in `src/` that import from `legacy/` to preserve behavior.
- When a module in `src/` is stable, move the implementation from `legacy/` into `src/` and update imports.
- Update `run_dev` scripts to use `src.main:app` as entrypoint once migrated.

Testing and linting
- Add small unit tests for service wrappers.
- Add CI to run flake8/ruff and pytest.

Security note
- Remove the real `.env` from repo history if it was ever committed. Keep `.env` in .gitignore and use `.env.example` for placeholders.

If you want, I can:
- Create the `src/` and `legacy/` folders and add the wrapper files above (non-destructive — they import existing code).
- Move one module (e.g. `app.py`) into `src/` and update run scripts.
- Add simple unit tests and a pre-commit config.

Tell me which step to perform first and I will apply it.  
