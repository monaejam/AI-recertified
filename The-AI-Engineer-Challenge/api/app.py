# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
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

# Initialize FastAPI application with a title
app = FastAPI(title="Enhanced AI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Global storage for vector stores and texts
vector_stores = {}
text_chunks = {}
PERSIST_DIRECTORY = ".chroma"

# Enums for better type safety
class ReasoningMode(str, Enum):
    NONE = "none"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STEP_BY_STEP = "step_by_step"

class StyleTone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"

class AccuracyLevel(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"

# Enhanced data model for chat requests
class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: Optional[str] = "gpt-4.1-mini"
    api_key: str
    reasoning_mode: Optional[ReasoningMode] = ReasoningMode.NONE
    style_tone: Optional[StyleTone] = StyleTone.PROFESSIONAL
    accuracy_level: Optional[AccuracyLevel] = AccuracyLevel.STANDARD
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    include_citations: Optional[bool] = False
    custom_instructions: Optional[str] = ""

# Advanced prompt templates
class PromptTemplates:
    @staticmethod
    def get_base_system_prompt(accuracy_level: AccuracyLevel, style_tone: StyleTone) -> str:
        base_prompt = """You are an intelligent AI assistant with the following capabilities:

**Accuracy & Reliability:**
- Always provide accurate, factual information
- If you're unsure about something, clearly state your uncertainty
- Cite sources when possible and appropriate
- Distinguish between facts, opinions, and speculation
- Avoid making up information or speculating beyond your knowledge

**Response Quality:**
- Provide comprehensive, well-structured responses
- Use clear, logical organization
- Include relevant examples when helpful
- Maintain consistency in your responses

**Communication Style:**
- Adapt your tone to be {style_tone}
- Be helpful, respectful, and professional
- Ask clarifying questions when needed
- Provide actionable advice when appropriate

**Special Instructions:**
{accuracy_instructions}

Remember: It's better to say "I don't know" than to provide incorrect information."""
        
        accuracy_instructions = {
            AccuracyLevel.STANDARD: "- Provide accurate information based on your training",
            AccuracyLevel.HIGH: "- Double-check facts before stating them\n- Provide context and qualifications for claims\n- Suggest verification sources when appropriate",
            AccuracyLevel.MAXIMUM: "- Only state information you are highly confident about\n- Always provide context and qualifications\n- Include specific sources or references when possible\n- Flag any areas of uncertainty clearly"
        }
        
        return base_prompt.format(
            style_tone=style_tone.value,
            accuracy_instructions=accuracy_instructions[accuracy_level]
        )

    @staticmethod
    def get_chain_of_thought_prompt() -> str:
        return """
**Chain-of-Thought Instructions:**
When answering complex questions, please follow this structured approach:

1. **Understand the Question**: First, clearly identify what is being asked
2. **Break Down the Problem**: Divide complex questions into smaller, manageable parts
3. **Think Step by Step**: Work through each part systematically
4. **Consider Multiple Perspectives**: Look at the question from different angles
5. **Reach a Conclusion**: Synthesize your analysis into a clear answer
6. **Validate Your Response**: Double-check that your answer addresses the original question

Please show your reasoning process as you work through the problem.
"""

    @staticmethod
    def get_style_guidance(style_tone: StyleTone) -> str:
        style_guides = {
            StyleTone.PROFESSIONAL: "Use formal, business-appropriate language. Be concise, clear, and objective. Avoid slang and casual expressions.",
            StyleTone.CASUAL: "Use friendly, conversational language. Feel free to use contractions and informal expressions while remaining helpful.",
            StyleTone.ACADEMIC: "Use scholarly language with precise terminology. Include citations and references when appropriate. Maintain academic rigor.",
            StyleTone.CREATIVE: "Use imaginative and expressive language. Feel free to use metaphors, analogies, and creative examples to illustrate points.",
            StyleTone.TECHNICAL: "Use precise technical terminology. Include specific details, specifications, and technical context. Be thorough and exact.",
            StyleTone.FRIENDLY: "Use warm, approachable language. Be encouraging and supportive. Use positive reinforcement and helpful suggestions."
        }
        return style_guides[style_tone]

# Enhanced chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        client = OpenAI(api_key=request.api_key)
        
        # Build enhanced system prompt
        system_prompt = PromptTemplates.get_base_system_prompt(
            request.accuracy_level, 
            request.style_tone
        )
        
        # Add reasoning mode if specified
        if request.reasoning_mode != ReasoningMode.NONE:
            system_prompt += PromptTemplates.get_chain_of_thought_prompt()
        
        # Add style guidance
        system_prompt += f"\n\n**Style Guidance:** {PromptTemplates.get_style_guidance(request.style_tone)}"
        
        # Add custom instructions if provided
        if request.custom_instructions:
            system_prompt += f"\n\n**Custom Instructions:** {request.custom_instructions}"
        
        # Add citation instructions if requested
        if request.include_citations:
            system_prompt += """
**Citation Instructions:**
- When providing factual information, include relevant sources or references
- Use [Source: description] format for citations
- If citing specific data or studies, provide enough context for verification
"""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.user_message}
        ]
        
        # Enhanced parameters
        params = {
            "model": request.model,
            "messages": messages,
            "stream": True,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        # Add advanced parameters for better accuracy
        if request.accuracy_level in [AccuracyLevel.HIGH, AccuracyLevel.MAXIMUM]:
            params.update({
                "top_p": 0.9,  # More focused sampling
                "frequency_penalty": 0.1,  # Reduce repetition
                "presence_penalty": 0.1,  # Encourage new topics
            })
        
        async def generate():
            try:
                stream = client.chat.completions.create(**params)
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"\n\n[Error: {str(e)}]"
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for advanced features
@app.post("/api/chat/advanced")
async def advanced_chat(request: ChatRequest):
    """Enhanced chat endpoint with additional features like response validation"""
    try:
        client = OpenAI(api_key=request.api_key)
        
        # First, generate the main response
        main_response = await chat(request)
        
        # For high accuracy requests, add validation
        if request.accuracy_level == AccuracyLevel.MAXIMUM:
            # Generate a validation prompt
            validation_prompt = f"""
Please review the following response for accuracy and completeness:

User Question: {request.user_message}
AI Response: [RESPONSE_PLACEHOLDER]

Please provide:
1. Accuracy assessment (1-10 scale)
2. Any factual errors or uncertainties
3. Missing important information
4. Suggestions for improvement
"""
            
            # This would require additional API calls for validation
            # For now, we'll return the main response
            return main_response
        
        return main_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoint
@app.get("/api/config")
async def get_config():
    """Return available configuration options"""
    return {
        "reasoning_modes": [mode.value for mode in ReasoningMode],
        "style_tones": [tone.value for tone in StyleTone],
        "accuracy_levels": [level.value for level in AccuracyLevel],
        "models": ["gpt-4.1-mini", "gpt-4", "gpt-3.5-turbo"],
        "default_settings": {
            "temperature": 0.7,
            "max_tokens": 2000,
            "reasoning_mode": ReasoningMode.NONE.value,
            "style_tone": StyleTone.PROFESSIONAL.value,
            "accuracy_level": AccuracyLevel.STANDARD.value
        }
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "features": ["enhanced_prompts", "chain_of_thought", "style_guidance", "accuracy_control"]}

# New models for PDF chat
class PDFChatRequest(BaseModel):
    message: str
    session_id: str
    api_key: str
    model: Optional[str] = "gpt-4.1-mini"

def get_encoding():
    """Get tiktoken encoding for text tokenization."""
    return tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    encoding = get_encoding()
    tokens = encoding.encode(text)
    chunks = []
    
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

def get_embeddings(texts: List[str], api_key: str) -> np.ndarray:
    """Get embeddings for texts using OpenAI API."""
    client = OpenAI(api_key=api_key)
    embeddings = []
    
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings.append(response.data[0].embedding)
    
    return np.array(embeddings, dtype=np.float32)

def process_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """Create FAISS index for vector similarity search."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def get_relevant_chunks(query: str, index: faiss.IndexFlatL2, chunks: List[str], 
                       query_embedding: np.ndarray, k: int = 3) -> List[str]:
    """Get most relevant chunks for a query."""
    # Reshape query embedding for FAISS
    query_embedding = query_embedding.reshape(1, -1)
    
    # Search for similar vectors
    distances, indices = index.search(query_embedding, k)
    
    # Get corresponding text chunks
    relevant_chunks = [chunks[i] for i in indices[0]]
    return relevant_chunks

# New endpoints for PDF functionality
@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), api_key: str = None):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    try:
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Process the PDF
            raw_text = process_pdf_text(temp_file.name)
            chunks = chunk_text(raw_text)
            
            # Generate embeddings
            embeddings = get_embeddings(chunks, api_key)
            
            # Create FAISS index
            index = create_faiss_index(embeddings)
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Store index and chunks
            vector_stores[session_id] = index
            text_chunks[session_id] = chunks
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return JSONResponse({
                "session_id": session_id,
                "message": "PDF processed successfully",
                "chunk_count": len(chunks)
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat-pdf")
async def chat_pdf(request: PDFChatRequest):
    if request.session_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first.")
    
    try:
        # Get the vector store and chunks for this session
        index = vector_stores[request.session_id]
        chunks = text_chunks[request.session_id]
        
        # Get query embedding
        query_embedding = get_embeddings([request.message], request.api_key)[0]
        
        # Get relevant chunks
        relevant_chunks = get_relevant_chunks(
            request.message, 
            index, 
            chunks, 
            query_embedding
        )
        
        # Prepare context
        context = "\n\n".join(relevant_chunks)
        
        # Initialize chat client
        client = OpenAI(api_key=request.api_key)
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful AI assistant that answers questions about the provided document.
Base your answers on the following context. If you cannot answer the question based on the context, say so.

Context:
{context}"""
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        async def generate():
            try:
                stream = client.chat.completions.create(
                    model=request.model,
                    messages=messages,
                    stream=True,
                    temperature=0.7
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"\n\n[Error: {str(e)}]"
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def cleanup():
    """Clean up resources on shutdown."""
    vector_stores.clear()
    text_chunks.clear()
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
