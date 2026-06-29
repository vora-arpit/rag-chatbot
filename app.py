from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from ingest import read_pdf, chunk_text, get_embedding, create_collection, store_chunks
from ingest_jd import ingest_jd
from matcher import run_matcher

app = FastAPI(title="ResumeRAG Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ResumeRAG Matcher is running!"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        text = read_pdf(tmp_path)
        chunks = chunk_text(text)
        create_collection()
        store_chunks(chunks)
        return {"message": f"✅ Resume ingested successfully! {len(chunks)} chunks stored."}
    finally:
        os.unlink(tmp_path)

@app.post("/upload-jd")
async def upload_jd(jd_text: str = Form(...)):
    ingest_jd(jd_text)
    return {"message": "✅ Job description ingested successfully!"}

@app.post("/match")
async def match():
    report = run_matcher()
    return {"report": report}