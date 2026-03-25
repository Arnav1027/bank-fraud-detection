#!/usr/bin/env python3
"""HTTP server for React SPA - serves index.html for all routes."""

import os
import sys
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class ReactSPAHandler(SimpleHTTPRequestHandler):
    """Handler for React Single Page Application."""
    
    def do_GET(self):
        """Handle GET requests, serving index.html for SPA routes."""
        # Get the requested path
        path = self.path.split('?')[0].split('#')[0]  # Remove query and fragment
        
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
    
    # Listen on all interfaces (needed for Docker/Railway)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, ReactSPAHandler)
    
    print(f'✅ Server started at http://0.0.0.0:{port}')
    print(f'📁 Serving from: {build_dir}')
    print('🔄 Routes → index.html (React Router handles them)')
    print('📁 Static files → served directly\n')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n✅ Server stopped')
        sys.exit(0)


if __name__ == '__main__':
    main()

