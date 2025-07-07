from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

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

@app.get("/api/config")
async def get_config(request: Request):
    """Get server configuration including the base URL."""
    base_url = str(request.base_url).rstrip('/')
    return {
        "api_url": base_url,
        "version": "1.0.0",
        "features": ["pdf_chat", "streaming", "vector_search"]
    }

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function entry point."""
    return app(request, context) 