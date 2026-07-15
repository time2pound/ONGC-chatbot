from app.rag import run_rag_pipeline

def get_response(
    question: str,
    model_name: str = "llama3.2:1b",
    temperature: float = 0.0,
    session_id: str = None
):
    """
    Standard interface to call the RAG pipeline.
    """
    return run_rag_pipeline(
        question=question,
        model_name=model_name,
        temperature=temperature,
        session_id=session_id
    )
