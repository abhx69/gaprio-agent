"""
quick_test.py - Quick API test
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🚀 Quick API Test")
    print("=" * 50)
    
    # Test 1: Health
    print("\n1. Testing health endpoint...")
    try:
        health = requests.get(f"{base_url}/health", timeout=5).json()
        print(f"   Health: {health}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Ask agent
    print("\n2. Testing ask-agent endpoint...")
    try:
        response = requests.post(
            f"{base_url}/ask-agent",
            json={
                "user_id": 1,
                "message": "Create a task for website review"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            # Save for debugging
            with open('debug_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("   Saved response to debug_response.json")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ask agent failed: {e}")
    
    # Test 3: List tables in database
    print("\n3. Checking database tables...")
    try:
        import mysql.connector
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Axkpq@8210'),
            database=os.getenv('DB_NAME', 'gaprio_agent_dev')
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"     - {table[0]}: {count} rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_api()