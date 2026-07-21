# AI Knowledge Assistant

An enterprise-grade, **fully offline** AI chatbot for querying internal documents (PDFs) using local Large Language Models via Ollama, RAG (Retrieval-Augmented Generation), and a premium web dashboard.

---

## Features

- **RAG Pipeline** — Answers questions grounded exclusively in indexed PDF documents
- **Local LLMs** — Runs fully offline using [Ollama](https://ollama.com) (`llama3.2`, `gemma3`, `qwen2.5`, etc.)
- **ChromaDB Vector Store** — Fast semantic similarity search with MMR retrieval
- **Premium Web Dashboard** — Chat, document management, analytics, and settings
- **Multi-session Chat History** — Sessions stored in browser `localStorage`
- **Document Ingestion** — Upload new PDFs via drag-and-drop; auto-indexed instantly
- **User Feedback System** — Thumbs up/down with optional comments; stored in SQLite
- **Analytics Dashboard** — Query counts, satisfaction rates, and recent activity logs
- **Voice Interface** — Speech-to-Text (input) and Text-to-Speech (output) via Web Speech API
- **Dark / Light Theme** — Toggle with persistent preference
- **Docker Deployment** — Full containerized deployment ready

---

## Project Structure

```
AI_CHATBOT/
│
├── app/                        # Core application modules
│   ├── __init__.py
│   ├── config.py               # Configuration: paths, models, settings
│   ├── chatbot.py              # Top-level chatbot interface
│   ├── memory.py               # Session-based chat memory
│   └── rag.py                  # RAG orchestration pipeline
│
├── utils/                      # Utility helpers
│   ├── __init__.py
│   ├── embeddings.py           # Singleton HuggingFace embedding provider
│   ├── loader.py               # PDF loading and text chunking
│   └── vectorstore.py          # ChromaDB CRUD operations
│
├── prompts/                    # System prompt templates
│   └── system_prompt.py
│
├── templates/
│   └── index.html              # Single-page dashboard UI
│
├── static/
│   ├── style.css               # Premium CSS styling (dark/light themes)
│   └── app.js                  # Frontend logic (chat, sessions, ingestion)
│
├── docs/                       # Indexed PDF documents (mounted volume)
│   └── sample_manual.pdf
│
├── chroma_db/                  # ChromaDB persistent vector store
│
├── main.py                     # FastAPI application entry point
├── ingest.py                   # Standalone PDF ingestion script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | 3.12/3.14 works fine |
| [Ollama](https://ollama.com) | Latest | Must be running locally |
| Git | Any | For version control |
| Docker (optional) | 24+ | For containerized deployment |

### Required Ollama Models

```bash
ollama pull llama3.2:1b        # Fast (recommended for dev)
ollama pull llama3.2           # Higher quality
ollama pull gemma3:1b          # Alternative
```

---

## Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd AI_CHATBOT
pip install -r requirements.txt
```

### 2. Ensure Ollama is Running

```bash
ollama serve   # Or start the Ollama desktop app
```

### 3. Index Documents (first time only)

If ChromaDB is not yet populated, run:

```bash
python ingest.py
```

Or upload PDFs directly from the **Documents** tab in the web UI.

### 4. Launch the Web App

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then open **http://127.0.0.1:8000** in your browser.

---

## Docker Deployment

```bash
# Build and start
docker-compose up --build

# Access at:
# http://localhost:8000
```

> The `chroma_db/`, `docs/`, and `feedback.db` are mounted as volumes so data persists across container restarts.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main web dashboard |
| `GET` | `/api/models` | Lists available Ollama models |
| `POST` | `/api/chat` | Send a question; returns answer + sources |
| `GET` | `/api/documents` | Lists indexed PDF files |
| `POST` | `/api/ingest` | Upload and index a new PDF |
| `POST` | `/api/feedback` | Submit thumbs up/down + comment |
| `GET` | `/api/analytics` | Returns satisfaction stats and activity logs |

### Example Chat Request

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the policy guidelines?", "model": "llama3.2:1b"}'
```

---

## Configuration

Settings are persisted in browser `localStorage` and can be adjusted in the **Settings** tab:

| Setting | Default | Description |
|---------|---------|-------------|
| LLM Model | `llama3.2:1b` | Active Ollama model |
| Temperature | `0.0` | Response creativity (0 = deterministic) |
| Retrieval K | `5` | Number of document chunks to retrieve |

Backend defaults live in [`app/config.py`](app/config.py).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Ollama (Llama 3.2, Gemma 3, Qwen 2.5) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector DB | ChromaDB |
| Orchestration | LangChain |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML5 / CSS3 / Vanilla JS |
| Feedback DB | SQLite |
| Deployment | Docker + Docker Compose |

---

## Developed By

**Enterprise AI Assistant Project**

