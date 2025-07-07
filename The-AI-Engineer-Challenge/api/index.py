from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import tempfile
from PyPDF2 import PdfReader
import numpy as np
import faiss
import tiktoken
import uuid
import shutil

# Initialize FastAPI application
app = FastAPI(title="Enhanced AI Chat API")

def get_allowed_origins():
    """Get allowed origins based on environment."""
    # Vercel deployment URL pattern
    vercel_url = os.environ.get('VERCEL_URL')
    if vercel_url:
        # Add both https and http variants of the Vercel URL
        return [
            f"https://{vercel_url}",
            f"http://{vercel_url}",
            "https://localhost:3000",
            "http://localhost:3000"
        ]
    return ["http://localhost:3000"]  # Default for local development

# Configure CORS middleware with dynamic origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all the existing code from app.py
# This is the same code that was in app.py, just moved here for Vercel compatibility

class ReasoningMode(str, Enum):
    NONE = "none"
    STEP_BY_STEP = "step_by_step"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"

class StyleTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CREATIVE = "creative"

class AccuracyLevel(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"

class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: str = "gpt-4.1-mini"
    api_key: str
    reasoning_mode: ReasoningMode = ReasoningMode.NONE
    style_tone: StyleTone = StyleTone.PROFESSIONAL
    accuracy_level: AccuracyLevel = AccuracyLevel.STANDARD
    temperature: float = 0.7
    max_tokens: int = 2000
    include_citations: bool = False
    custom_instructions: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None
    citations: Optional[List[str]] = None

# Global storage for PDF sessions (in production, use a proper database)
pdf_sessions: Dict[str, Dict[str, Any]] = {}

def get_reasoning_prompt(mode: ReasoningMode) -> str:
    """Get the reasoning prompt based on the selected mode."""
    prompts = {
        ReasoningMode.NONE: "",
        ReasoningMode.STEP_BY_STEP: "Please think through this step by step:",
        ReasoningMode.CHAIN_OF_THOUGHT: "Let me think through this carefully:",
        ReasoningMode.TREE_OF_THOUGHTS: "Let me explore different approaches to this:"
    }
    return prompts.get(mode, "")

def get_style_prompt(tone: StyleTone) -> str:
    """Get the style prompt based on the selected tone."""
    prompts = {
        StyleTone.PROFESSIONAL: "Respond in a professional and business-like manner.",
        StyleTone.CASUAL: "Respond in a casual and conversational tone.",
        StyleTone.FRIENDLY: "Respond in a warm and friendly manner.",
        StyleTone.FORMAL: "Respond in a formal and academic tone.",
        StyleTone.CREATIVE: "Respond in a creative and imaginative way."
    }
    return prompts.get(tone, "")

def get_accuracy_prompt(level: AccuracyLevel) -> str:
    """Get the accuracy prompt based on the selected level."""
    prompts = {
        AccuracyLevel.STANDARD: "Provide accurate and reliable information.",
        AccuracyLevel.HIGH: "Provide highly accurate information with thorough verification.",
        AccuracyLevel.MAXIMUM: "Provide maximum accuracy with extensive verification and multiple sources."
    }
    return prompts.get(level, "")

@app.get("/api/config")
async def get_config(request: Request):
    """Get server configuration including the base URL."""
    base_url = str(request.base_url).rstrip('/')
    return {
        "api_url": base_url,
        "version": "1.0.0",
        "features": ["pdf_chat", "streaming", "vector_search"]
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with reasoning, style, and accuracy controls."""
    try:
        client = OpenAI(api_key=request.api_key)
        
        # Build the system message with all enhancements
        system_parts = [request.developer_message]
        
        if request.reasoning_mode != ReasoningMode.NONE:
            system_parts.append(get_reasoning_prompt(request.reasoning_mode))
        
        system_parts.append(get_style_prompt(request.style_tone))
        system_parts.append(get_accuracy_prompt(request.accuracy_level))
        
        if request.custom_instructions:
            system_parts.append(f"Additional instructions: {request.custom_instructions}")
        
        system_message = " ".join(system_parts)
        
        # Prepare the user message
        user_message = request.user_message
        if request.include_citations:
            user_message += " Please include relevant citations and sources in your response."
        
        def generate_response():
            try:
                response = client.chat.completions.create(
                    model=request.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"Error: {str(e)}"
        
        return StreamingResponse(generate_response(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), api_key: str = None):
    """Upload and process a PDF file for chat."""
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Create a temporary directory for this session
        session_id = str(uuid.uuid4())
        temp_dir = tempfile.mkdtemp()
        
        # Save the uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from PDF
        reader = PdfReader(file_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Simple text chunking (in production, use more sophisticated chunking)
        chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
        
        # Store session data
        pdf_sessions[session_id] = {
            "chunks": chunks,
            "temp_dir": temp_dir,
            "filename": file.filename
        }
        
        return {"session_id": session_id, "chunks_count": len(chunks)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/api/chat-pdf")
async def chat_pdf(request: dict):
    """Chat with the uploaded PDF content."""
    session_id = request.get("session_id")
    message = request.get("message")
    api_key = request.get("api_key")
    
    if not all([session_id, message, api_key]):
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    if session_id not in pdf_sessions:
        raise HTTPException(status_code=404, detail="PDF session not found")
    
    try:
        client = OpenAI(api_key=api_key)
        session_data = pdf_sessions[session_id]
        
        # Create context from PDF chunks
        context = "\n".join(session_data["chunks"][:5])  # Use first 5 chunks for context
        
        def generate_response():
            try:
                response = client.chat.completions.create(
                    model=request.get("model", "gpt-4.1-mini"),
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant. Use the following PDF content to answer questions:\n\n{context}"},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"Error: {str(e)}"
        
        return StreamingResponse(generate_response(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function entry point."""
    return app(request, context) 