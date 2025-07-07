from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Get the base URL from environment or construct it
        vercel_url = os.environ.get('VERCEL_URL', 'localhost:3000')
        base_url = f"https://{vercel_url}" if vercel_url != 'localhost:3000' else f"http://{vercel_url}"
        
        response = {
            "api_url": base_url,
            "version": "1.0.0",
            "features": ["pdf_chat", "streaming", "vector_search"],
            "endpoint": "config"
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