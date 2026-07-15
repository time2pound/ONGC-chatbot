import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

def load_and_split_pdf(file_path: str):
    """
    Load a PDF document and split it into chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
        
    print(f"Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")
    
    print(f"Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")
    
    # Store source filename relative to docs
    for chunk in chunks:
        # Normalize the source path to just the filename to make display pretty
        if "source" in chunk.metadata:
            chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])
            
    return chunks
