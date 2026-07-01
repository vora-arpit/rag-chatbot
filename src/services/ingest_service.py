from fastapi import UploadFile
import tempfile
import os

# Use existing legacy implementation for now (non-destructive)
from legacy import ingest as legacy_ingest

async def ingest_resume_file(file: UploadFile) -> int:
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
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

def ingest_jd_text(jd_text: str):
    from legacy import ingest_jd as legacy_jd
    from fastapi import HTTPException
    try:
        legacy_jd.ingest_jd(jd_text)
    except Exception as e:
        # Surface a clear HTTP error for the API caller (and preserve original message)
        raise HTTPException(status_code=500, detail=f"Failed to ingest JD: {e}")

