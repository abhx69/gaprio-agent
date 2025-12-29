"""
start_server.py - Clean server startup
"""

import os
import time
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def check_dependencies():
    """Check if all dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        print("✅ Ollama is running")
    except:
        print("⚠️  Ollama may not be running. Start with: ollama serve")
    
    # Check MySQL
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Axkpq@8210'),
            database=os.getenv('DB_NAME', 'gaprio_agent_dev')
        )
        conn.close()
        print("✅ MySQL is accessible")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
    
    print("✅ All dependencies checked")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Gaprio Agent Server...")
    print("=" * 50)
    
    # Import and start
    try:
        import uvicorn
        from main import app
        
        port = int(os.getenv('APP_PORT', 8000))
        
        print(f"\n✅ Server starting on http://localhost:{port}")
        print("   Press Ctrl+C to stop\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=True  # Auto-reload on changes
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        print("\n💡 Try running: python main.py directly")

if __name__ == "__main__":
    check_dependencies()
    time.sleep(1)
    start_server()