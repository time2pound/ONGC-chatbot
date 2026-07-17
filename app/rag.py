import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from utils.vectorstore import get_retriever
from prompts.system_prompt import DEFAULT_SYSTEM_PROMPT
from app.memory import get_chat_memory
from app.config import OLLAMA_API_BASE, DEFAULT_LLM_MODEL

def run_rag_pipeline(
    question: str,
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.0,
    session_id: str = None,
    k: int = 5
):
    """
    Executes the complete RAG pipeline:
    1. Retrieves relevant documents from ChromaDB.
    2. Formats retrieved chunks as context.
    3. Merges system prompts and chat history.
    4. Calls the local Ollama LLM.
    5. Stores the exchange in chat memory.
    """
    # 1. Retrieve relevant documents
    retriever = get_retriever(k=k)
    docs = []
    try:
        docs = retriever.invoke(question)
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        
    # 2. Format retrieved documents for context
    context_str = ""
    sources = []
    for i, doc in enumerate(docs):
        page = doc.metadata.get("page", "Unknown")
        source = doc.metadata.get("source", "Unknown")
        # Ensure page numbers are 1-based or readable (sometimes page is 0-indexed)
        # We can display what is in the metadata
        if isinstance(page, int):
            page_str = f"Page {page + 1}"
        else:
            page_str = f"Page {page}"
            
        context_str += f"[Source: {source}, {page_str}]\n{doc.page_content}\n\n"
        sources.append({
            "id": i + 1,
            "filename": source,
            "page": page_str,
            "snippet": doc.page_content
        })
        

        
    # 3. Handle session history
    memory = get_chat_memory()
    history = []
    if session_id:
        history = memory.get_history(session_id)
        
    # Construct the system prompt with context
    system_prompt = DEFAULT_SYSTEM_PROMPT.format(context=context_str if context_str else "No documents found in database.")
    
    # 4. Construct message chain
    lc_messages = [SystemMessage(content=system_prompt)]
    
    # Append recent chat history
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
            
    # Append current user question
    lc_messages.append(HumanMessage(content=question))
    
    # 5. Invoke LLM
    print(f"Invoking model '{model_name}' on Ollama API base: {OLLAMA_API_BASE}")
    try:
        llm = ChatOllama(
            base_url=OLLAMA_API_BASE,
            model=model_name,
            temperature=temperature,
            keep_alive="30m"
        )
        response = llm.invoke(lc_messages)
        answer = response.content
    except Exception as e:
        print(f"Ollama invocation error: {e}")
        answer = f"Error communicating with local Ollama: {str(e)}"
        
    # 6. Save exchange to memory if session exists and request succeeded
    if session_id and not answer.startswith("Error communicating"):
        memory.add_message(session_id, "user", question)
        memory.add_message(session_id, "assistant", answer)
        
    return {
        "answer": answer,
        "sources": sources
    }

def run_rag_pipeline_stream(
    question: str,
    model_name: str = DEFAULT_LLM_MODEL,
    temperature: float = 0.0,
    session_id: str = None,
    k: int = 5
):
    """
    Executes the complete RAG pipeline and yields tokens as a stream of JSON lines.
    """
    # 1. Retrieve relevant documents
    retriever = get_retriever(k=k)
    docs = []
    try:
        docs = retriever.invoke(question)
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        
    # 2. Format retrieved documents for context
    context_str = ""
    sources = []
    for i, doc in enumerate(docs):
        page = doc.metadata.get("page", "Unknown")
        source = doc.metadata.get("source", "Unknown")
        if isinstance(page, int):
            page_str = f"Page {page + 1}"
        else:
            page_str = f"Page {page}"
            
        context_str += f"[Source: {source}, {page_str}]\n{doc.page_content}\n\n"
        sources.append({
            "id": i + 1,
            "filename": source,
            "page": page_str,
            "snippet": doc.page_content
        })
        

        
    # Yield sources immediately as the first chunk
    yield json.dumps({"type": "sources", "sources": sources}) + "\n"
    
    # 3. Handle session history
    memory = get_chat_memory()
    history = []
    if session_id:
        history = memory.get_history(session_id)
        
    system_prompt = DEFAULT_SYSTEM_PROMPT.format(context=context_str if context_str else "No documents found in database.")
    
    lc_messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=question))
    
    # 4. Invoke LLM and stream tokens
    try:
        llm = ChatOllama(
            base_url=OLLAMA_API_BASE,
            model=model_name,
            temperature=temperature,
            keep_alive="30m"
        )
        full_response = ""
        for chunk in llm.stream(lc_messages):
            token = chunk.content
            full_response += token
            yield json.dumps({"type": "token", "token": token}) + "\n"
            
        # 5. Save to memory on successful complete stream
        if session_id and full_response:
            memory.add_message(session_id, "user", question)
            memory.add_message(session_id, "assistant", full_response)
            
    except Exception as e:
        print(f"Ollama stream error: {e}")
        err_msg = f"Error communicating with local Ollama: {str(e)}"
        yield json.dumps({"type": "error", "error": err_msg}) + "\n"
