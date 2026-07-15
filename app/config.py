import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
DOCUMENTS_DIR = os.path.join(BASE_DIR, "docs")
FEEDBACK_DB_PATH = os.path.join(BASE_DIR, "feedback.db")

# Model settings
DEFAULT_LLM_MODEL = "llama3.2:1b"
DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Ingestion settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Ollama API settings
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# Ensure documents folder exists
if not os.path.exists(DOCUMENTS_DIR):
    os.makedirs(DOCUMENTS_DIR)
