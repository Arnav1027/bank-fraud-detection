#!/usr/bin/env python3
"""Simple HTTP server for React SPA with proper routing fallback."""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class SPAHandler(SimpleHTTPRequestHandler):
    """Custom handler for Single Page Application routing."""

    def do_GET(self):
        """Handle GET requests with fallback to index.html for React routing."""
        # Get the requested path
        request_path = self.path.split('?')[0].split('#')[0]  # Remove query and fragment
        
        # Translate to filesystem path
        file_path = self.translate_path(request_path)
        
        # Check if it's a real file that exists
        if os.path.isfile(file_path):
            # Real file exists, serve it
            self.path = request_path
            return SimpleHTTPRequestHandler.do_GET(self)
        
        # Not a file - it's a route. Serve index.html for React Router
        self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def end_headers(self):
        """Add cache control headers."""
        if self.path.endswith('index.html') or self.path == '/':
            # Don't cache index.html
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        # Cache everything else (CSS, JS, images)
        super().end_headers()


if __name__ == '__main__':
    # Change to build directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'build'))
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
    server_address = ('127.0.0.1', port)
    
    httpd = HTTPServer(server_address, SPAHandler)
    print(f'🚀 Server running at http://127.0.0.1:{port}')
    print(f'📁 Serving: {os.getcwd()}')
    print('Press Ctrl+C to stop\n')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n✅ Server stopped')
        sys.exit(0)

