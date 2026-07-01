from fastapi import APIRouter, UploadFile, File, Form
from src.services.ingest_service import ingest_resume_file, ingest_jd_text
from src.services.match_service import run_match

router = APIRouter()

@router.get("/api/health")
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

