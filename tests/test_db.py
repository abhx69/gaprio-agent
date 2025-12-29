"""
test_db.py - Database connection test
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    """Test database connection"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 3306),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'gaprio_agent_dev')
        )
        
        if conn.is_connected():
            print("✅ Connected to MySQL!")
            
            # Check tables
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n📊 Tables in database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Create tables if they don't exist
            create_tables_if_not_exist(cursor)
            
            cursor.close()
            conn.close()
            print("\n✅ All tests passed!")
            
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")

def create_tables_if_not_exist(cursor):
    """Create necessary tables if they don't exist"""
    
    # Create agent_chat_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_chat_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✅ agent_chat_logs table created/verified")
    
    # Create ai_pending_actions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_pending_actions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            provider ENUM('google', 'asana'),
            action_type VARCHAR(50),
            draft_payload JSON,
            status ENUM('pending', 'approved', 'rejected', 'executed') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_at TIMESTAMP NULL
        )
    """)
    print("  ✅ ai_pending_actions table created/verified")

if __name__ == "__main__":
    print("Testing Gaprio Agent Database Connection...")
    test_connection()