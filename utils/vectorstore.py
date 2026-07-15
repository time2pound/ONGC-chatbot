import os
from langchain_community.vectorstores import Chroma
from utils.embeddings import get_embeddings
from app.config import CHROMA_DB_DIR

_db = None

def get_vectorstore():
    """
    Get the vector database instance. Reuses the connection if loaded.
    """
    global _db
    if _db is None:
        embeddings = get_embeddings()
        print(f"Connecting to ChromaDB at: {CHROMA_DB_DIR}")
        _db = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )
    return _db

def get_retriever(k=5):
    """
    Get a retriever instance with Maximal Marginal Relevance (MMR) search.
    """
    db = get_vectorstore()
    return db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 20
        }
    )

def add_documents_to_db(chunks):
    """
    Add document chunks to ChromaDB.
    """
    db = get_vectorstore()
    print(f"Adding {len(chunks)} chunks to vector store...")
    db.add_documents(chunks)
    print("Documents successfully added to DB!")

def get_all_document_names():
    """
    Retrieve unique source filenames from the docs/ directory.
    """
    from app.config import DOCUMENTS_DIR
    try:
        if not os.path.exists(DOCUMENTS_DIR):
            return []
        # Return all PDF files in docs folder
        files = [f for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".pdf")]
        return files
    except Exception as e:
        print(f"Error retrieving documents from docs folder: {e}")
        return []
