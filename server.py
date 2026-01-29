#!/usr/bin/env python3
"""
HTTPS Web Server for GPS & Phone Inclination Logger
Serves measures.html over HTTPS with self-signed certificate

Hints:
- Free blocked port: sudo fuser -k <port>/tcp
"""

import os
import ssl
import http.server
import socketserver
import subprocess
import socket
from pathlib import Path
import mimetypes

# Configuration
PORT = 8444
CERT_FILE = 'cert.pem'
KEY_FILE = 'key.pem'
HTML_FILE_DATA_COLLECT = 'measures.html'
HTML_FILE_SHOW_MAP = 'map.html'
DIR_RECEIVED_FILES = 'received_data'
DIR_CREATED_FILES = 'created_maps'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve measures.html for root path
        if self.path == '/' or self.path == '':
            self.path = '/' + HTML_FILE_DATA_COLLECT
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers to allow requests from different origins
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Use different caching policies for PWA assets so they can be cached by the browser
        pwa_assets = ('/sw.js', '/manifest.json', '/icon.svg', '/icon.png')
        css_files = ('.css',)
        if any(self.path.endswith(a) for a in pwa_assets) or any(self.path.endswith(c) for c in css_files):
            # Cache static assets for a long time (service worker, icons, and stylesheets)
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        else:
            # Default: do not cache HTML responses while developing
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def do_OPTIONS(self):
        # Respond to CORS preflight
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # Handle POST to /data_collector
        if self.path != '/data_collector':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        try:
            import json
            import time
            import csv
            import subprocess
            from datetime import datetime

            # Parse the JSON payload
            payload = json.loads(body.decode('utf-8'))
            data = payload.get('data', [])

            # Save received payload as a timestamped file under 'received/'
            os.makedirs(DIR_RECEIVED_FILES, exist_ok=True)
            timestamp_str = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            fname = f"{DIR_RECEIVED_FILES}/data_{timestamp_str}.json"
            with open(fname, 'wb') as f:
                f.write(body)

            # Generate CSV from data
            csv_filename = f"{DIR_RECEIVED_FILES}/data_{timestamp_str}.csv"
            map_filename = None
            if data:
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['Index', 'DateTime', 'Latitude', 'Longitude', 'Inclination(degrees)'])
                    writer.writeheader()
                    for row in data:
                        writer.writerow({
                            'Index': row.get('index', ''),
                            'DateTime': row.get('dateTime', ''),
                            'Latitude': row.get('latitude', ''),
                            'Longitude': row.get('longitude', ''),
                            'Inclination(degrees)': row.get('inclination', '')
                        })
                print(f"[DATA RECEIVED] Generated CSV: {csv_filename}")

                # Generate map using csv_to_map.py
                os.makedirs(DIR_CREATED_FILES, exist_ok=True)
                map_filename = f"{DIR_CREATED_FILES}/map_{timestamp_str}.html"
                result = subprocess.run(
                    ['python3', 'csv_to_map.py', csv_filename, map_filename],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"[MAP GENERATED] {map_filename}")
                    # Return the URL path for the frontend to access
                    map_url = f"/{map_filename}"
                else:
                    print(f"[MAP GENERATION FAILED] {result.stderr}")
                    map_url = None

            print(f"[DATA RECEIVED] Saved to {fname}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            resp = {'status': 'ok', 'received': fname, 'map': map_url if 'map_url' in locals() else None}
            self.wfile.write(json.dumps(resp).encode())
        except Exception as e:
            print(f"Error while handling POST /data_collector: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.log_date_time_string()}] {format % args}")

    def list_directory(self, path):
        """Restrict directory listing: allow only DIR_CREATED_FILES, forbid others."""
        try:
            # Resolve real paths
            requested = os.path.realpath(path)
            allowed = os.path.realpath(os.path.join(os.getcwd(), DIR_CREATED_FILES))

            # Allow listing only when requested path is inside the created_maps directory
            if os.path.commonpath([requested, allowed]) == allowed:
                return super().list_directory(path)
        except Exception:
            pass

        # Deny directory listing for all other directories
        self.send_error(403, "Directory listing is prohibited")
        return None


def generate_self_signed_cert():
    """Generate a self-signed certificate if it doesn't exist"""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"✓ Using existing certificates: {CERT_FILE}, {KEY_FILE}")
        return True
    
    print("Generating self-signed certificate...")
    
    # Get hostname or use localhost
    try:
        hostname = socket.gethostname()
    except:
        hostname = 'localhost'
    
    # Generate self-signed certificate using openssl
    cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', KEY_FILE, '-out', CERT_FILE,
        '-days', '365', '-nodes',
        '-subj', f'/CN={hostname}'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Generated self-signed certificate: {CERT_FILE}, {KEY_FILE}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating certificate: {e}")
        print("Make sure 'openssl' is installed on your system.")
        return False
    except FileNotFoundError:
        print("✗ 'openssl' command not found. Please install OpenSSL.")
        print("  On Ubuntu/Debian: sudo apt-get install openssl")
        print("  On macOS: brew install openssl")
        print("  On Windows: https://slproweb.com/products/Win32OpenSSL.html")
        return False
    
    return True


def start_server():
    """Start the HTTPS web server"""
    
    # Check if HTML file exists
    if not os.path.exists(HTML_FILE_DATA_COLLECT):
        print(f"✗ Error: {HTML_FILE_DATA_COLLECT} not found in current directory!")
        return
    
    # Generate certificates
    if not generate_self_signed_cert():
        return
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    
    # Create server
    try:
        # Ensure common MIME types are registered so assets are served correctly
        mimetypes.add_type('application/javascript', '.js')
        # Use manifest MIME type if available
        mimetypes.add_type('application/manifest+json', '.json')
        mimetypes.add_type('text/css', '.css')

        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            
            print("\n" + "="*60)
            print("HTTPS Web Server Started")
            print("="*60)
            print(f"📁 Serving: {HTML_FILE_DATA_COLLECT}")
            print(f"🔒 Server: https://localhost:{PORT}")
            print(f"📱 Mobile: https://<your-ip>:{PORT}")
            print(f"🔐 Certificate: {CERT_FILE}")
            print("\nTo find your local IP address:")
            print("  - Linux/macOS: ifconfig | grep inet")
            print("  - Windows: ipconfig")
            print("\n⚠️  Warning: Using self-signed certificate.")
            print("   Your browser will show a security warning - this is normal.")
            print("   Click 'Advanced' and 'Proceed' to access the page.")
            print("\n✓ Server running. Press Ctrl+C to stop.\n")
            print("="*60 + "\n")
            
            httpd.serve_forever()
    
    except PermissionError:
        print(f"✗ Error: Cannot bind to port {PORT}.")
        if PORT < 1024:
            print(f"  Ports below 1024 require root access.")
            print(f"  Try: sudo python3 server.py")
        else:
            print(f"  Port {PORT} may already be in use.")
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped.")
    except Exception as e:
        print(f"✗ Error starting server: {e}")


if __name__ == '__main__':
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    start_server()
