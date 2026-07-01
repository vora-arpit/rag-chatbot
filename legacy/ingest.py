from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import pymupdf
import uuid

from config import settings

# Load credentials and configuration from environment
GEMINI_API_KEY = settings.GEMINI_API_KEY
QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
PDF_PATH = settings.PDF_PATH
COLLECTION_NAME = settings.COLLECTION_NAME
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
VECTOR_SIZE = settings.VECTOR_SIZE

# Validate required values early
if not all([GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    raise RuntimeError(
        "Missing required environment variables. Copy `.env.example` to `.env` and fill in your keys."
    )

# --- Clients ---
gemini = genai.Client(api_key=GEMINI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# --- Step 1: Read PDF ---
def read_pdf(path):
    doc = pymupdf.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Step 2: Split into chunks ---
def chunk_text(text):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

# --- Step 3: Get embedding from Gemini ---
def get_embedding(text):
    response = gemini.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values

# --- Step 4: Create collection in Qdrant ---
def create_collection():
    if not qdrant.collection_exists(collection_name=COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print("Collection created!")
    else:
        print("Collection already exists, skipping creation.")

# --- Step 5: Store chunks in Qdrant ---
def store_chunks(chunks):
    points = []
    for i, chunk in enumerate(chunks):
        print(f"Embedding chunk {i+1}/{len(chunks)}...")
        embedding = get_embedding(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        ))
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(chunks)} chunks in Qdrant!")

if __name__ == "__main__":
    print("Reading PDF...")
    text = read_pdf(PDF_PATH)
    print(f"Total characters: {len(text)}")
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    create_collection()
    store_chunks(chunks)

