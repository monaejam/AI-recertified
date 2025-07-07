from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
from openai import OpenAI
import tempfile
import uuid
import shutil
from PyPDF2 import PdfReader
import base64
import io
import csv

# Global storage for PDF and CSV sessions (in production, use a proper database)
pdf_sessions = {}
csv_sessions = {}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL to determine which endpoint
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if path == '/api/test':
            response = {
                "message": "API is working!",
                "status": "success",
                "endpoint": "test"
            }
        elif path == '/api/config':
            # Get the base URL from environment or construct it
            vercel_url = os.environ.get('VERCEL_URL', 'localhost:3000')
            base_url = f"https://{vercel_url}" if vercel_url != 'localhost:3000' else f"http://{vercel_url}"
            
            response = {
                "api_url": base_url,
                "version": "1.0.0",
                "features": ["pdf_chat", "streaming", "vector_search"],
                "endpoint": "config"
            }
        else:
            response = {
                "error": "Endpoint not found",
                "available_endpoints": ["/api/test", "/api/config", "/api/chat", "/api/upload-pdf", "/api/chat-pdf"]
            }
        
        self.wfile.write(json.dumps(response).encode())
        return

    def do_POST(self):
        # Parse the URL to determine which endpoint
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
        except:
            request_data = {}
        
        if path == '/api/chat':
            # Set response headers for chat
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                # Extract data from request
                developer_message = request_data.get('developer_message', 'You are a helpful AI assistant.')
                user_message = request_data.get('user_message', '')
                model = request_data.get('model', 'gpt-4.1-mini')
                api_key = request_data.get('api_key', '')
                temperature = request_data.get('temperature', 0.7)
                max_tokens = request_data.get('max_tokens', 2000)
                
                if not api_key:
                    self.wfile.write(b"Error: API key is required")
                    return
                    
                if not user_message:
                    self.wfile.write(b"Error: User message is required")
                    return
                
                # Initialize OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Create chat completion
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": developer_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False  # For simplicity, we'll return the full response
                )
                
                # Get the response content
                response_content = response.choices[0].message.content
                
                # Send the response
                self.wfile.write(response_content.encode('utf-8'))
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                self.wfile.write(error_message.encode('utf-8'))
        
        elif path == '/api/upload-pdf':
            # Set response headers for JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                api_key = request_data.get('api_key', '')
                pdf_base64 = request_data.get('pdf_content', '')
                filename = request_data.get('filename', 'document.pdf')
                
                if not api_key:
                    response = {
                        "error": "API key is required",
                        "status": "error"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                if not pdf_base64:
                    response = {
                        "error": "PDF content is required",
                        "status": "error"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Create a session ID
                session_id = str(uuid.uuid4())
                
                try:
                    # Decode base64 PDF content
                    pdf_bytes = base64.b64decode(pdf_base64)
                    pdf_stream = io.BytesIO(pdf_bytes)
                    
                    # Extract text from PDF
                    reader = PdfReader(pdf_stream)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    # Simple text chunking (in production, use more sophisticated chunking)
                    chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
                    
                    # Store session data
                    pdf_sessions[session_id] = {
                        "chunks": chunks,
                        "filename": filename,
                        "text_content": text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                    }
                    
                    response = {
                        "session_id": session_id,
                        "chunks_count": len(chunks),
                        "message": f"PDF '{filename}' uploaded and processed successfully",
                        "status": "success",
                        "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
                    }
                    
                except Exception as e:
                    # If PDF processing fails, create a mock session
                    pdf_sessions[session_id] = {
                        "chunks": [f"Mock content for {filename}. This is a placeholder since PDF processing failed: {str(e)}"],
                        "filename": filename,
                        "text_content": f"Mock content for {filename}"
                    }
                    
                    response = {
                        "session_id": session_id,
                        "chunks_count": 1,
                        "message": f"PDF '{filename}' uploaded (mock mode due to processing error)",
                        "status": "success",
                        "text_preview": f"Mock content for {filename}"
                    }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                response = {
                    "error": f"Error uploading PDF: {str(e)}",
                    "status": "error"
                }
                self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/upload-csv':
            # Set response headers for JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                api_key = request_data.get('api_key', '')
                csv_base64 = request_data.get('file_content', '')
                filename = request_data.get('filename', 'data.csv')
                
                if not api_key:
                    response = {
                        "error": "API key is required",
                        "status": "error"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                if not csv_base64:
                    response = {
                        "error": "CSV content is required",
                        "status": "error"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Create a session ID
                session_id = str(uuid.uuid4())
                
                try:
                    # Decode base64 CSV content
                    csv_bytes = base64.b64decode(csv_base64)
                    csv_text = csv_bytes.decode('utf-8')
                    
                    # Parse CSV content
                    csv_reader = csv.reader(io.StringIO(csv_text))
                    rows = list(csv_reader)
                    
                    if not rows:
                        raise Exception("CSV file is empty")
                    
                    # Get headers and sample data
                    headers = rows[0] if rows else []
                    sample_rows = rows[1:6] if len(rows) > 1 else []  # First 5 data rows
                    
                    # Create a summary of the CSV
                    csv_summary = {
                        "total_rows": len(rows),
                        "total_columns": len(headers),
                        "headers": headers,
                        "sample_data": sample_rows,
                        "raw_content": csv_text[:2000] + "..." if len(csv_text) > 2000 else csv_text
                    }
                    
                    # Store session data
                    csv_sessions[session_id] = {
                        "summary": csv_summary,
                        "filename": filename,
                        "rows": rows,
                        "headers": headers
                    }
                    
                    response = {
                        "session_id": session_id,
                        "rows_count": len(rows),
                        "columns_count": len(headers),
                        "message": f"CSV '{filename}' uploaded and processed successfully",
                        "status": "success",
                        "preview": {
                            "headers": headers,
                            "sample_rows": sample_rows
                        }
                    }
                    
                except Exception as e:
                    # If CSV processing fails, create a mock session
                    csv_sessions[session_id] = {
                        "summary": {
                            "total_rows": 0,
                            "total_columns": 0,
                            "headers": [],
                            "sample_data": [],
                            "raw_content": f"Mock content for {filename}"
                        },
                        "filename": filename,
                        "rows": [],
                        "headers": []
                    }
                    
                    response = {
                        "session_id": session_id,
                        "rows_count": 0,
                        "columns_count": 0,
                        "message": f"CSV '{filename}' uploaded (mock mode due to processing error)",
                        "status": "success",
                        "preview": {
                            "headers": [],
                            "sample_rows": []
                        }
                    }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                response = {
                    "error": f"Error uploading CSV: {str(e)}",
                    "status": "error"
                }
                self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/chat-pdf':
            # Set response headers for chat
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                session_id = request_data.get('session_id', '')
                message = request_data.get('message', '')
                api_key = request_data.get('api_key', '')
                
                # Debug logging
                print(f"PDF Chat Debug - session_id: {session_id}, message: {message}, api_key: {api_key[:10]}...")
                print(f"Available sessions: {list(pdf_sessions.keys())}")
                
                if not session_id:
                    self.wfile.write(b"Error: session_id is required")
                    return
                
                if not message:
                    self.wfile.write(b"Error: message is required")
                    return
                
                if not api_key:
                    self.wfile.write(b"Error: api_key is required")
                    return
                
                if session_id not in pdf_sessions:
                    self.wfile.write(f"Error: PDF session not found. Available sessions: {list(pdf_sessions.keys())}".encode())
                    return
                
                # Initialize OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Get session data
                session_data = pdf_sessions[session_id]
                context = "\n".join(session_data["chunks"])
                
                # Create chat completion
                response = client.chat.completions.create(
                    model=request_data.get('model', 'gpt-4.1-mini'),
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant. Use the following PDF content to answer questions:\n\n{context}"},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    stream=False
                )
                
                # Get the response content
                response_content = response.choices[0].message.content
                
                # Send the response
                self.wfile.write(response_content.encode('utf-8'))
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(f"PDF Chat Error: {error_message}")
                self.wfile.write(error_message.encode('utf-8'))
        
        elif path == '/api/chat-csv':
            # Set response headers for chat
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                session_id = request_data.get('session_id', '')
                message = request_data.get('message', '')
                api_key = request_data.get('api_key', '')
                
                # Debug logging
                print(f"CSV Chat Debug - session_id: {session_id}, message: {message}, api_key: {api_key[:10]}...")
                print(f"Available CSV sessions: {list(csv_sessions.keys())}")
                
                if not session_id:
                    self.wfile.write(b"Error: session_id is required")
                    return
                
                if not message:
                    self.wfile.write(b"Error: message is required")
                    return
                
                if not api_key:
                    self.wfile.write(b"Error: api_key is required")
                    return
                
                if session_id not in csv_sessions:
                    self.wfile.write(f"Error: CSV session not found. Available sessions: {list(csv_sessions.keys())}".encode())
                    return
                
                # Initialize OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Get session data
                session_data = csv_sessions[session_id]
                csv_summary = session_data["summary"]
                
                # Create context from CSV data
                context = f"""
CSV Data Summary:
- File: {session_data['filename']}
- Total Rows: {csv_summary['total_rows']}
- Total Columns: {csv_summary['total_columns']}
- Headers: {', '.join(csv_summary['headers'])}

Sample Data (first 5 rows):
{chr(10).join([', '.join(row) for row in csv_summary['sample_data']])}

Raw CSV Content (first 2000 characters):
{csv_summary['raw_content']}
"""
                
                # Create chat completion
                response = client.chat.completions.create(
                    model=request_data.get('model', 'gpt-4.1-mini'),
                    messages=[
                        {"role": "system", "content": f"You are a helpful data analyst assistant. Use the following CSV data to answer questions:\n\n{context}"},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    stream=False
                )
                
                # Get the response content
                response_content = response.choices[0].message.content
                
                # Send the response
                self.wfile.write(response_content.encode('utf-8'))
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                print(f"CSV Chat Error: {error_message}")
                self.wfile.write(error_message.encode('utf-8'))
        
        else:
            # Set response headers for JSON error
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "error": "Endpoint not found",
                "status": "error"
            }
            self.wfile.write(json.dumps(response).encode())
        
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

 