import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from app.config import DEFAULT_EMBED_MODEL

_embeddings = None

def get_embeddings():
    """
    Get the embedding model instance. Reuses the model if already loaded.
    """
    global _embeddings
    if _embeddings is None:
        print(f"Loading Embedding Model: {DEFAULT_EMBED_MODEL}...")
        _embeddings = HuggingFaceEmbeddings(
            model_name=DEFAULT_EMBED_MODEL,
            model_kwargs={"local_files_only": True}
        )
    return _embeddings
