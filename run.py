"""
run.py - Simple server runner
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🚀 Starting Gaprio Agent Server")
    print("=" * 50)
    
    # Check database connection first
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Axkpq@8210'),
            database=os.getenv('DB_NAME', 'gaprio_agent_dev')
        )
        conn.close()
        print("✅ Database: Connected")
    except Exception as e:
        print(f"❌ Database: Failed - {e}")
        return
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        print("✅ Ollama: Running")
    except:
        print("⚠️  Ollama: Not detected (AI features may be limited)")
    
    # Start server
    print("\n🌐 Starting web server...")
    print(f"   Server will be available at: http://localhost:{os.getenv('APP_PORT', 8000)}")
    print("   Press Ctrl+C to stop\n")
    
    # Import and run
    try:
        import uvicorn
        from main import app
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=int(os.getenv('APP_PORT', 8000)),
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server failed: {e}")

if __name__ == "__main__":
    main()