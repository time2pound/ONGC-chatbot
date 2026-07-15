from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = db.as_retriever(search_kwargs={"k":5})

question = input("Enter Question: ")

docs = retriever.invoke(question)

print("\nRetrieved Documents:\n")

for i, doc in enumerate(docs):
    print("="*70)
    print(f"Document {i+1}")
    print("="*70)
    print(doc.page_content)
    print()