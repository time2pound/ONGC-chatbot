import os
# Force HuggingFace and Transformers to run offline
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DOCS_DIR = "docs"
CHROMA_DB_DIR = "chroma_db"

print("==================================================")
print("       Bulk PDF Ingestion")
print("==================================================")

# 1. Initialize Embeddings Model (Offline mode)
print("Loading HuggingFace Embeddings model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"local_files_only": True}
)

# 2. Connect to ChromaDB
print("Connecting to ChromaDB...")
db = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings
)

# 3. Check already indexed files in ChromaDB
print("Checking indexed documents...")
try:
    collection = db.get()
    metadatas = collection.get("metadatas", [])
    indexed_files = {os.path.basename(m.get("source")) for m in metadatas if m and m.get("source")}
except Exception as e:
    print(f"No existing collections or error reading DB: {e}")
    indexed_files = set()

if indexed_files:
    print(f"Already indexed documents in DB: {list(indexed_files)}")
else:
    print("No documents currently indexed in ChromaDB.")

# 4. Scan docs/ folder for PDF files
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]
if not pdf_files:
    print(f"\nNo PDF files found in '{DOCS_DIR}/' folder.")
    print("Please copy your PDF manual files into the 'docs/' directory and run this script again.")
    exit(0)

# 5. Ingest new files
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

new_files_count = 0
for filename in pdf_files:
    if filename in indexed_files:
        print(f"\nSkipping '{filename}' (already indexed).")
        continue

    file_path = os.path.join(DOCS_DIR, filename)
    print(f"\nProcessing '{filename}'...")
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"  - Loaded {len(documents)} pages.")

        chunks = text_splitter.split_documents(documents)
        # Set source to just the basename for pretty rendering
        for chunk in chunks:
            if "source" in chunk.metadata:
                chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])

        print(f"  - Created {len(chunks)} chunks.")
        print(f"  - Adding to ChromaDB...")
        db.add_documents(chunks)
        print(f"  - ✅ Successfully indexed '{filename}'!")
        new_files_count += 1
    except Exception as e:
        print(f"  - ❌ Failed to index '{filename}': {e}")

print("\n==================================================")
print(f"Ingestion complete. Indexed {new_files_count} new file(s).")
print("==================================================")