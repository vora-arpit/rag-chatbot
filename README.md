# 📄 RAG Chatbot

An end-to-end **Retrieval-Augmented Generation (RAG)** system that lets you chat with any PDF document using natural language. Built with Google Gemini for embeddings and generation, and Qdrant as the vector database.

## 🚀 Demo

Ask questions like:
- *"What are Alex's skills?"*
- *"Where did he study?"*
- *"What projects has he worked on?"*

And get accurate answers grounded in the actual document — no hallucinations.

## 🧠 How It Works
Below is the end-to-end workflow in diagram form.

```mermaid
flowchart TD
  A[PDF] --> B[Text Extraction]
  B --> C[Chunking]
  C --> D[Gemini Embeddings]
  D --> E[Qdrant Vector DB]

  subgraph Query Flow
    F[User Question] --> G[Embed Question]
    G --> H[Similarity Search]
    H --> I[Top Chunks]
    I --> J[Gemini LLM]
    J --> K[Answer]
  end

  E --> H
```

If your viewer doesn't render Mermaid, here's a plain-text alternative:

```
PDF → Text Extraction → Chunking → Gemini Embeddings → Qdrant Vector DB

User Question → Embed Question → Similarity Search → Top Chunks → Gemini LLM → Answer
```

## 🛠️ Development / Run locally

1. Create a virtual environment and install dependencies:

PowerShell:

```powershell
.\run_dev.ps1
```

Unix/macOS:

```bash
./run_dev.sh
```

Or manually:

```bash
python -m venv .venv
source .venv/bin/activate   # or .\.venv\Scripts\Activate.ps1 on Windows PowerShell
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

2. Create `.env` from `.env.example` and fill in your API keys.

3. If `uvicorn` isn't found, run it via the module: `python -m uvicorn app:app --reload`.
