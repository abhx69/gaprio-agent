"""
setup_database.py - Complete database setup script
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    print("🔧 Setting up Gaprio Agent Database...")
    
    # Database configuration
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'Axkpq@8210'),
    }
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("✅ Connected to MySQL server")
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS gaprio_agent_dev")
        cursor.execute("USE gaprio_agent_dev")
        print("✅ Database created/selected")
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_connections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                provider ENUM('google', 'asana') NOT NULL,
                provider_user_id VARCHAR(255),
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at TIMESTAMP,
                metadata JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_provider (user_id, provider)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS agent_chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_user_chat (user_id, created_at)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ai_pending_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                provider ENUM('google', 'asana'),
                action_type VARCHAR(50),
                draft_payload JSON,
                status ENUM('pending', 'approved', 'rejected', 'executed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_user_status (user_id, status)
            )
            """
        ]
        
        for i, table_sql in enumerate(tables, 1):
            cursor.execute(table_sql)
            print(f"✅ Table {i} created/verified")
        
        # Insert sample user if not exists
        cursor.execute("""
            INSERT IGNORE INTO users (id, email, full_name) 
            VALUES (1, 'test@example.com', 'Test User')
        """)
        
        # Insert sample Asana connection
        cursor.execute("""
            INSERT IGNORE INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'asana', 'pat_1ASANA_SAMPLE_TOKEN_123')
            ON DUPLICATE KEY UPDATE access_token = VALUES(access_token)
        """)
        
        # Insert sample Google connection
        cursor.execute("""
            INSERT IGNORE INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'google', 'ya29.GOOGLE_SAMPLE_TOKEN_456')
            ON DUPLICATE KEY UPDATE access_token = VALUES(access_token)
        """)
        
        conn.commit()
        
        # Verify data
        print("\n📊 Verifying data...")
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"  Users: {len(users)} records")
        
        cursor.execute("SELECT * FROM user_connections")
        connections = cursor.fetchall()
        print(f"  Connections: {len(connections)} records")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n✅ Database setup complete! {len(tables)} tables created:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database is ready!")
        print("\nNext steps:")
        print("1. Restart your server: Ctrl+C then 'python main.py'")
        print("2. Run: python -c \"import requests; print(requests.get('http://localhost:8000/health').json())\"")
        print("3. Database should show 'connected'")
        
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check password in .env file")
        print("3. Try: mysql -u root -p")
        print("4. Common passwords: '', 'root', 'password', '123456'")

if __name__ == "__main__":
    setup_database()