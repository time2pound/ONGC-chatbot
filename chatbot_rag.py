from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

# ===============================
# Load Embedding Model
# ===============================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ===============================
# Load Chroma Database
# ===============================

print("Loading ChromaDB...")

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20
    }
)

# ===============================
# Load Llama
# ===============================

print("Loading Llama...")

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
    num_predict=200,
    keep_alive="30m"
)

print("\n===========================================")
print("        AI KNOWLEDGE ASSISTANT")
print("Type 'exit' to quit")
print("===========================================")

while True:

    question = input("\nYou : ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    try:

        print("\nSearching document...")

        docs = retriever.invoke(question)

        print(f"Retrieved {len(docs)} document(s).\n")

        if len(docs) == 0:
            print("AI : I could not find anything.")
            continue

        print("========== RETRIEVED DOCUMENT ==========\n")

        for i, doc in enumerate(docs):

            print(f"Document {i+1}")

            print(doc.page_content[:400])

            print("\nPage :", doc.metadata.get("page", "Unknown"))

            print("-" * 70)

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
You are an expert AI Knowledge Assistant.

Answer ONLY using the information given in the context.

Never make up an answer.

If the answer is not present,
reply exactly:

I could not find the answer in the document.

=========================
CONTEXT
=========================

{context}

=========================
QUESTION
=========================

{question}

=========================
ANSWER
=========================
"""

        print("\nSending prompt to Llama...\n")

        response = llm.invoke(prompt)

        print("\n===================================")
        print("AI ANSWER")
        print("===================================\n")

        print(response.content)

    except Exception as e:

        print("\nERROR\n")

        print(e)