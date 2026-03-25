#!/usr/bin/env python3
"""HTTP server for React SPA with API proxy - serves index.html for all routes."""

import os
import sys
import mimetypes
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urljoin


class ReactSPAHandler(SimpleHTTPRequestHandler):
    """Handler for React Single Page Application with API proxy."""
    
    def do_GET(self):
        """Handle GET requests, proxying /api/* and serving SPA routes."""
        # Get the requested path
        path = self.path.split('?')[0].split('#')[0]  # Remove query and fragment
        
        # Proxy API requests to backend
        if path.startswith('/api/'):
            self.proxy_api_request(self.path)
            return
        
        # Special case: root path should serve index.html
        if path == '/':
            index_path = Path.cwd() / 'index.html'
            if index_path.is_file():
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
        
        # Map path to file system
        file_path = Path.cwd() / path.lstrip('/')
        
        # Check if it's a real file (JS, CSS, JSON, images, etc.)
        if file_path.is_file():
            # Serve the actual file
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(str(file_path))
            self.send_header('Content-type', mime_type or 'text/plain')
            self.send_header('Content-Length', file_path.stat().st_size)
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
            return
        
        # Not a real file - it's a route. Serve index.html
        index_path = Path.cwd() / 'index.html'
        if index_path.is_file():
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            with open(index_path, 'rb') as f:
                self.wfile.write(f.read())
            return
        
        # No index.html found
        self.send_error(404, 'File not found')
    
    def do_POST(self):
        """Handle POST requests, proxying API requests."""
        path = self.path.split('?')[0]
        if path.startswith('/api/'):
            self.proxy_api_request(self.path, method='POST')
            return
        self.send_error(404, 'Not found')
    
    def proxy_api_request(self, path, method='GET'):
        """Proxy API request to backend server."""
        try:
            # Get backend URL from environment
            backend_port = int(os.environ.get('BACKEND_PORT', '8001'))
            backend_url = f'http://localhost:{backend_port}{path}'
            
            # Read request body if present
            content_length = self.headers.get('Content-Length')
            body = None
            if content_length:
                body = self.rfile.read(int(content_length))
            
            # Make request to backend
            headers = dict(self.headers)
            headers.pop('Host', None)  # Remove Host header
            
            if method == 'POST':
                response = requests.post(backend_url, data=body, headers=headers, timeout=30)
            else:
                response = requests.get(backend_url, headers=headers, timeout=30)
            
            # Send response back to client
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_error(502, f'Bad Gateway: {str(e)}')


def main():
    # Move to build directory
    script_dir = Path(__file__).parent
    build_dir = script_dir / 'build'
    os.chdir(build_dir)
    
    # Get port from argument or use PORT env var or default to 3001
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = int(os.environ.get('PORT', 3001))
    
    # Listen on all interfaces (needed for Docker/Render)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, ReactSPAHandler)
    
    backend_port = os.environ.get('BACKEND_PORT', '8001')
    print(f'✅ Frontend server started at http://0.0.0.0:{port}')
    print(f'📁 Serving from: {build_dir}')
    print(f'🔗 Proxying /api/* to http://localhost:{backend_port}')
    print('🔄 Routes → index.html (React Router handles them)')
    print('📁 Static files → served directly\n')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n✅ Server stopped')
        sys.exit(0)


if __name__ == '__main__':
    main()

