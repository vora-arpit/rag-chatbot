from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import settings
import uuid

GEMINI_API_KEY = settings.GEMINI_API_KEY
QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
VECTOR_SIZE = settings.VECTOR_SIZE
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP
JD_COLLECTION = "jd_chunks"

if not all([GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    raise RuntimeError("Missing required environment variables.")

gemini = genai.Client(api_key=GEMINI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def chunk_text(text):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def get_embedding(text):
    response = gemini.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values

def create_jd_collection():
    if qdrant.collection_exists(collection_name=JD_COLLECTION):
        qdrant.delete_collection(collection_name=JD_COLLECTION)
        print("Old JD collection deleted.")
    qdrant.create_collection(
        collection_name=JD_COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print("JD collection created!")

def ingest_jd(jd_text):
    create_jd_collection()
    chunks = chunk_text(jd_text)
    points = []
    for i, chunk in enumerate(chunks):
        print(f"Embedding JD chunk {i+1}/{len(chunks)}...")
        embedding = get_embedding(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        ))
    qdrant.upsert(collection_name=JD_COLLECTION, points=points)
    print(f"Stored {len(chunks)} JD chunks in Qdrant!")

if __name__ == "__main__":
    print("Paste the job description below.")
    print("When done, type END on a new line and press Enter:\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    jd_text = "\n".join(lines)
    if not jd_text.strip():
        print("No text entered.")
    else:
        ingest_jd(jd_text)

