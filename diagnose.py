"""
diagnose.py - Diagnostic script
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

print("🔍 Running Diagnostics...")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
env_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_NAME']
for var in env_vars:
    value = os.getenv(var)
    print(f"   {var}: {value}")

# Check password (masked)
password = os.getenv('DB_PASSWORD', '')
print(f"   DB_PASSWORD: {'[SET]' if password else '[NOT SET]'} ({len(password)} chars)")

# Test database connection
print("\n2. Database Connection Test:")
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'gaprio_agent_dev')
    )
    
    cursor = conn.cursor()
    
    # Check database
    cursor.execute("SELECT DATABASE()")
    db = cursor.fetchone()[0]
    print(f"   ✅ Connected to database: {db}")
    
    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"   📊 Tables found: {len(tables)}")
    for table in tables:
        cursor.execute(f"DESCRIBE {table[0]}")
        columns = cursor.fetchall()
        print(f"     - {table[0]}: {len(columns)} columns")
    
    # Check sample data
    print(f"\n3. Sample Data Check:")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"   Users: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM user_connections")
    conn_count = cursor.fetchone()[0]
    print(f"   Connections: {conn_count}")
    
    cursor.execute("SELECT provider, LENGTH(access_token) FROM user_connections")
    tokens = cursor.fetchall()
    for provider, length in tokens:
        print(f"     {provider}: token length {length}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"   ❌ Connection failed: {e}")
    
    # Try without database
    print(f"\n   Trying without specific database...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        print(f"   ✅ Can connect to MySQL server")
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = cursor.fetchall()
        print(f"   Available databases: {[db[0] for db in dbs]}")
        
        cursor.close()
        conn.close()
    except Exception as e2:
        print(f"   ❌ Cannot connect to MySQL at all: {e2}")

print("\n" + "=" * 60)
print("✅ Diagnostics complete!")