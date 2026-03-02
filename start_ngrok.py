#!/usr/bin/env python3
"""
Start Ngrok tunnels for both frontend and backend
Provides public URLs for public access
"""
import os
import sys
import time
from pyngrok import ngrok

# Kill any existing tunnels
ngrok.kill()
time.sleep(1)

# Start tunnels
print("\n🚀 Starting Ngrok tunnels...\n")

backend_tunnel = ngrok.connect(7777, "http")
frontend_tunnel = ngrok.connect(3001, "http")

print("=" * 70)
print("✅ PUBLIC URLS READY")
print("=" * 70)
print(f"\n📱 FRONTEND (React App):  {frontend_tunnel}")
print(f"🔧 BACKEND (API):        {backend_tunnel}")
print("\nUse these URLs from anywhere in the world!")
print("\nTo stop: Press Ctrl+C")
print("=" * 70 + "\n")

try:
    # Keep tunnels running
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("\n\n⏹️  Stopping Ngrok tunnels...")
    ngrok.kill()
    sys.exit(0)
