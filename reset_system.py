"""
reset_system.py - Complete system reset
"""

import os
import subprocess
import time
import sys

def reset_database():
    """Reset the database"""
    print("🔄 Resetting database...")
    
    import mysql.connector
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Axkpq@8210')
        )
        
        cursor = conn.cursor()
        
        # Drop and recreate database
        cursor.execute("DROP DATABASE IF EXISTS gaprio_agent_dev")
        cursor.execute("CREATE DATABASE gaprio_agent_dev")
        cursor.execute("USE gaprio_agent_dev")
        
        # Create tables
        tables = [
            """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE user_connections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                provider ENUM('google', 'asana') NOT NULL,
                provider_user_id VARCHAR(255),
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at TIMESTAMP,
                metadata JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE agent_chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE ai_pending_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                provider ENUM('google', 'asana'),
                action_type VARCHAR(50),
                draft_payload JSON,
                status ENUM('pending', 'approved', 'rejected', 'executed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP NULL
            )
            """
        ]
        
        for sql in tables:
            cursor.execute(sql)
        
        # Insert sample data
        cursor.execute("""
            INSERT INTO users (id, email, full_name) 
            VALUES (1, 'test@example.com', 'Test User')
        """)
        
        cursor.execute("""
            INSERT INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'asana', 'pat_sample_asana_token')
        """)
        
        cursor.execute("""
            INSERT INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'google', 'google_sample_token')
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database reset complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

def start_server():
    """Start the server"""
    print("\n🚀 Starting server...")
    
    try:
        # Import and run server
        import uvicorn
        from main import app
        
        port = 8000
        print(f"Server running on http://localhost:{port}")
        
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server failed: {e}")

def test_system():
    """Test the system"""
    print("\n🧪 Testing system...")
    time.sleep(2)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health check: {response.json()}")
        
        # Test ask-agent
        response = requests.post(
            "http://localhost:8000/ask-agent",
            json={"user_id": 1, "message": "Create a test task"},
            timeout=10
        )
        print(f"Ask agent: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ System is working!")
        else:
            print(f"⚠️  System test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🎯 Gaprio Agent System Reset")
    print("=" * 50)
    
    # Reset database
    if reset_database():
        print("\n✅ Ready to start server")
        print("   Run: python main.py")
        print("   Or: python start_server.py")
        
        # Ask to test
        test = input("\nTest now? (y/n): ")
        if test.lower() == 'y':
            # Start server in background
            print("Starting server for test...")
            
            import threading
            import time
            
            def run_server():
                import uvicorn
                from main import app
                uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
            
            # Start server in thread
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            time.sleep(3)  # Wait for server to start
            test_system()
    else:
        print("\n❌ Reset failed. Check your MySQL connection.")