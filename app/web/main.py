from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from loguru import logger
import os

from app.config import settings
from app.core.document_processor import DocumentProcessor
from app.core.vector_store import VectorStoreManager
from app.core.llm_manager import LLMManager
from app.core.rag_pipeline import RAGPipeline

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="TUK-ConvoSearch: AI Student Support Assistant",
    version=settings.VERSION
)

# Initialize components (singleton pattern)
vector_store = None
llm_manager = None
rag_pipeline = None

class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = "anonymous"

class DocumentUploadRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    helpful: bool
    feedback_text: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup"""
    global vector_store, llm_manager, rag_pipeline
    
    try:
        logger.info("Starting TUK-ConvoSearch...")
        
        # Initialize components
        vector_store = VectorStoreManager(settings)
        llm_manager = LLMManager(settings)
        rag_pipeline = RAGPipeline(settings, vector_store, llm_manager)
        
        logger.info("TUK-ConvoSearch started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main interface"""
    with open("app/web/templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/query")
async def query_endpoint(request: QueryRequest):
    """Handle user queries"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        result = rag_pipeline.process_query(request.question)
        
        # Log the query
        logger.info(f"User query: {request.question}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_documents():
    """Upload and process documents"""
    try:
        # Check if raw documents exist
        raw_dir = settings.RAW_DOCS_DIR
        if not os.path.exists(raw_dir):
            return {"message": f"No documents found in {raw_dir}. Please add documents first."}
        
        # Process documents
        processor = DocumentProcessor(settings)
        documents = processor.process_directory(raw_dir)
        
        if not documents:
            return {"message": "No documents processed. Check file formats."}
        
        # Convert to vector store format
        doc_dicts = []
        for i, doc in enumerate(documents):
            doc_dicts.append({
                "text": doc.page_content,
                "metadata": doc.metadata
            })
        
        # Add to vector store
        vector_store.add_documents(doc_dicts)
        
        return {
            "message": f"Successfully processed {len(documents)} document chunks",
            "chunks": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-info")
async def get_system_info():
    """Get system information"""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    info = rag_pipeline.get_system_info()
    return info

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on responses"""
    try:
        # Log feedback (in production, store in database)
        logger.info(f"Feedback received - Helpful: {feedback.helpful}, Query: {feedback.query[:50]}...")
        
        # Here you could store feedback in a database for analysis
        # feedback_db.add(feedback)
        
        return {"message": "Feedback received. Thank you!"}
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )