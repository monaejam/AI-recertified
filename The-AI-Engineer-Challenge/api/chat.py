from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        # Set response headers
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
        
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return 