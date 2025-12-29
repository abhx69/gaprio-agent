import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def fix_database():
    print("🔧 Fixing Database Connection...")
    
    # Get database configuration
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 3306),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'Axkpq@8210'),
    }
    
    try:
        # Connect without database first
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("✅ Connected to MySQL server")
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS gaprio_agent_dev")
        print("✅ Database created/verified")
        
        # Use the database
        cursor.execute("USE gaprio_agent_dev")
        
        # Create tables
        tables_sql = [
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
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS agent_chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                executed_at TIMESTAMP NULL
            )
            """
        ]
        
        for i, sql in enumerate(tables_sql, 1):
            cursor.execute(sql)
            print(f"✅ Table {i} created/verified")
        
        # Insert sample data
        cursor.execute("""
            INSERT IGNORE INTO users (id, email, full_name) 
            VALUES (1, 'test@example.com', 'Test User')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'asana', 'pat_sample_token')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO user_connections (user_id, provider, access_token) 
            VALUES (1, 'google', 'google_sample_token')
        """)
        
        conn.commit()
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Database contains {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database fixed successfully!")
        
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MySQL is running")
        print("2. Check your password in .env file")
        print("3. Try connecting with: mysql -u root -p")
        print("4. Your password might be different than 'Axkpq@8210'")

if __name__ == "__main__":
    fix_database()