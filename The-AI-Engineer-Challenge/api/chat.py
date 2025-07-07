from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from typing import Optional
from enum import Enum

# Initialize FastAPI application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: str = "gpt-4.1-mini"
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint."""
    try:
        client = OpenAI(api_key=request.api_key)
        
        def generate_response():
            try:
                response = client.chat.completions.create(
                    model=request.model,
                    messages=[
                        {"role": "system", "content": request.developer_message},
                        {"role": "user", "content": request.user_message}
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

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function entry point."""
    return app(request, context) 