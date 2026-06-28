# 📄 RAG Resume Chatbot

An end-to-end **Retrieval-Augmented Generation (RAG)** system that lets you chat with any PDF document using natural language. Built with Google Gemini for embeddings and generation, and Qdrant as the vector database.

## 🚀 Demo

Ask questions like:
- *"What are Arpit's skills?"*
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
