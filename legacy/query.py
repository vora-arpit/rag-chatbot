from google import genai
from qdrant_client import QdrantClient

from config import settings
from google.genai.errors import ClientError

# Load credentials and configuration from environment
GEMINI_API_KEY = settings.GEMINI_API_KEY
QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
COLLECTION_NAME = settings.COLLECTION_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
LLM_MODEL = settings.LLM_MODEL
TOP_K = settings.TOP_K

# Validate required values early
if not all([GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    raise RuntimeError(
        "Missing required environment variables. Copy `.env.example` to `.env` and fill in your keys."
    )

# --- Clients ---
gemini = genai.Client(api_key=GEMINI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# --- Step 1: Embed the question ---
def embed_query(question):
    response = gemini.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question
    )
    return response.embeddings[0].values

# --- Step 2: Search Qdrant for relevant chunks ---
def search(question):
    vector = embed_query(question)
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=TOP_K
    ).points
    return [r.payload["text"] for r in results]

# --- Step 3: Ask Gemini with context ---
def ask(question):
    chunks = search(question)
    context = "\n\n".join(chunks)
    prompt = f"""You are a helpful assistant. Answer the question using only the context provided below.
If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:"""
    try:
        response = gemini.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        return response.text
    except ClientError as e:
        # Print helpful debug info about quota / response
        try:
            print("API error:", e.status_code, getattr(e, "response_json", None))
        except Exception:
            print("API error:", str(e))
        raise

if __name__ == "__main__":
    print("✅ RAG system ready! Type 'exit' to quit.\n")
    while True:
        question = input("You: ")
        if question.lower() == "exit":
            break
        answer = ask(question)
        print(f"\nAssistant: {answer}\n")

