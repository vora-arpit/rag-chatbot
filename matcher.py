from google import genai
from groq import Groq
from qdrant_client import QdrantClient
from config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
LLM_MODEL = settings.LLM_MODEL
TOP_K = settings.TOP_K

RESUME_COLLECTION = settings.COLLECTION_NAME
JD_COLLECTION = "jd_chunks"

if not all([GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, GROQ_API_KEY]):
    raise RuntimeError("Missing required environment variables.")

gemini = genai.Client(api_key=GEMINI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

def get_embedding(text):
    response = gemini.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values

def search_collection(collection_name, query_text, top_k=TOP_K):
    vector = get_embedding(query_text)
    results = qdrant.query_points(
        collection_name=collection_name,
        query=vector,
        limit=top_k
    ).points
    return [r.payload["text"] for r in results]

def generate_match_report(resume_chunks, jd_chunks):
    resume_context = "\n\n".join(resume_chunks)
    jd_context = "\n\n".join(jd_chunks)

    prompt = f"""You are an expert technical recruiter and career coach.

Below is a candidate's resume content and a job description.
Analyze them carefully and generate a structured match report.

--- RESUME ---
{resume_context}

--- JOB DESCRIPTION ---
{jd_context}

Generate a report with exactly these sections:

1. MATCH SCORE: Give a percentage (0-100%) based on how well the resume matches the job.

2. MATCHED SKILLS: List skills/experience from the resume that directly match the job requirements. For each one, cite the exact part of the resume it came from.

3. TRANSFERABLE SKILLS: List skills from the resume that are not an exact match but are relevant and transferable. Explain why each one is transferable.

4. MISSING SKILLS: List requirements from the job description that are NOT found in the resume at all.

5. GAP QUESTIONS: For each missing skill, generate one specific interview question a recruiter should ask to check if the candidate actually has that experience but didn't mention it.

6. OVERALL RECOMMENDATION: One paragraph summary — should the recruiter move forward with this candidate? Why or why not?

Be specific. Always cite which part of the resume supports each claim."""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def run_matcher():
    print("\n🔍 Searching resume and job description...\n")

    # Get all JD chunks to use as search queries
    jd_chunks = search_collection(JD_COLLECTION, "skills experience requirements qualifications", top_k=5)
    resume_chunks = search_collection(RESUME_COLLECTION, "skills experience projects education", top_k=5)

    print("✅ Retrieved relevant chunks from both documents.")
    print("\n⚙️  Generating match report...\n")

    report = generate_match_report(resume_chunks, jd_chunks)
    return report

if __name__ == "__main__":
    report = run_matcher()
    print("\n" + "="*60)
    print("📊 RESUME MATCH REPORT")
    print("="*60)
    print(report)
    print("="*60)

    # Save report to file
    with open("match_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ Report saved to match_report.txt")