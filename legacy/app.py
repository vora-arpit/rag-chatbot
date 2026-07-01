from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from legacy import ingest as ingest_module
from legacy import ingest_jd as ingest_jd_module
from legacy import matcher as matcher_module

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
        text = ingest_module.read_pdf(tmp_path)
        chunks = ingest_module.chunk_text(text)
        ingest_module.create_collection()
        ingest_module.store_chunks(chunks)
        return {"message": f"✅ Resume ingested successfully! {len(chunks)} chunks stored."}
    finally:
        os.unlink(tmp_path)

@app.post("/upload-jd")
async def upload_jd(jd_text: str = Form(...)):
    ingest_jd_module.ingest_jd(jd_text)
    return {"message": "✅ Job description ingested successfully!"}

@app.post("/match")
async def match():
    report = matcher_module.run_matcher()
    return {"report": report}

