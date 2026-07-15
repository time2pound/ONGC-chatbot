import os
import sqlite3
import shutil
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import httpx

from app.config import OLLAMA_API_BASE, DEFAULT_LLM_MODEL, FEEDBACK_DB_PATH, DOCUMENTS_DIR
from app.rag import run_rag_pipeline
from utils.vectorstore import get_all_document_names, add_documents_to_db
from utils.loader import load_and_split_pdf

# Initialize FastAPI application
app = FastAPI(title="ONGC Enterprise AI Chatbot", version="1.0.0")

# Setup templates and static file directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Feedback Database
def init_feedback_db():
    try:
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                question TEXT,
                answer TEXT,
                rating TEXT,
                comment TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing feedback database: {e}")

init_feedback_db()

# Request schemas
class ChatRequest(BaseModel):
    question: str
    model: Optional[str] = DEFAULT_LLM_MODEL
    temperature: Optional[float] = 0.0
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    answer: str
    rating: str  # 'up' or 'down'
    comment: Optional[str] = ""

# API Endpoints

@app.get("/")
async def home():
    """
    Serves the main Chatbot dashboard user interface.
    """
    return FileResponse("templates/index.html")

@app.get("/api/models")
async def get_models():
    """
    Fetches the list of available LLM models from local Ollama.
    Falls back to a standard default list if Ollama is not active.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_API_BASE}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                # Filter out embedding models to make list clean
                models = [m for m in models if "embed" not in m]
                return {"models": models}
    except Exception as e:
        print(f"Could not connect to Ollama tags endpoint: {e}")
        
    # Return locally discovered models from our previous command check
    return {"models": ["llama3.2:1b", "llama3.2:latest", "gemma3:1b", "qwen2.5:0.5b"]}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Processes chat prompt through the RAG pipeline.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        res = run_rag_pipeline(
            question=request.question,
            model_name=request.model,
            temperature=request.temperature,
            session_id=request.session_id
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    """
    Lists unique documents indexed in ChromaDB.
    """
    docs = get_all_document_names()
    return {"documents": docs}

@app.post("/api/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Uploads a new PDF document, splits it into chunks, and indexes it in ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Save the file to docs/
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse and chunk document
        chunks = load_and_split_pdf(file_path)
        
        # Add to ChromaDB
        add_documents_to_db(chunks)
        
        return {"status": "success", "filename": file.filename, "chunks_created": len(chunks)}
    except Exception as e:
        # Clean up file on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Saves user thumbs up/down rating and remarks.
    """
    try:
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (session_id, question, answer, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (request.session_id, request.question, request.answer, request.rating, request.comment))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")

@app.get("/api/analytics")
async def get_analytics():
    """
    Computes chat statistics and rating logs for the dashboard analytics.
    """
    try:
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Total chats
        cursor.execute("SELECT COUNT(*) as total FROM feedback")
        total_chats = cursor.fetchone()["total"]
        
        # 2. Positive vs negative feedback
        cursor.execute("SELECT COUNT(*) as positive FROM feedback WHERE rating = 'up'")
        positive = cursor.fetchone()["positive"]
        
        cursor.execute("SELECT COUNT(*) as negative FROM feedback WHERE rating = 'down'")
        negative = cursor.fetchone()["negative"]
        
        # 3. Recent logs
        cursor.execute("SELECT timestamp, question, rating, comment FROM feedback ORDER BY timestamp DESC LIMIT 10")
        recent = [dict(row) for row in cursor.fetchall()]
        
        # 4. Comments summary
        cursor.execute("SELECT comment, timestamp FROM feedback WHERE comment != '' ORDER BY timestamp DESC LIMIT 5")
        comments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Calculate rating percentage
        success_rate = 0
        if positive + negative > 0:
            success_rate = round((positive / (positive + negative)) * 100)
            
        return {
            "total_chats": total_chats,
            "likes": positive,
            "dislikes": negative,
            "satisfaction_rate": f"{success_rate}%" if positive + negative > 0 else "N/A",
            "recent_activity": recent,
            "user_comments": comments
        }
    except Exception as e:
        print(f"Analytics query error: {e}")
        return {
            "total_chats": 0,
            "likes": 0,
            "dislikes": 0,
            "satisfaction_rate": "N/A",
            "recent_activity": [],
            "user_comments": []
        }
