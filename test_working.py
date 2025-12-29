"""
test_working.py - Simple working test
"""

import requests
import json
import time

def test():
    print("🧪 Testing Gaprio Agent")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("Waiting for server to be ready...")
    time.sleep(3)
    
    # 1. Health check
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health = response.json()
        print(f"   ✅ Status: {health.get('status')}")
        print(f"   📊 Database: {health.get('database')}")
        print(f"   🤖 Ollama: {health.get('ollama')}")
    except Exception as e:
        print(f"   ❌ Server not responding: {e}")
        return
    
    # 2. Test with simple message
    print("\n2. Testing AI Agent:")
    
    test_messages = [
        "Create a task for website review",
        "Send email to team@example.com about meeting",
        "Hello, how are you?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: '{message}'")
        
        try:
            response = requests.post(
                f"{base_url}/ask-agent",
                json={"user_id": 1, "message": message},
                timeout=15  # Longer timeout for LLM
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     ✅ Success!")
                print(f"     Message: {result.get('message')}")
                
                plan = result.get('plan', [])
                if isinstance(plan, list) and plan:
                    print(f"     Actions generated: {len(plan)}")
                    for action in plan:
                        print(f"       • {action.get('tool', 'unknown')}")
                elif plan:
                    print(f"     Plan: {plan}")
                else:
                    print(f"     No actions needed")
            else:
                print(f"     ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"     ⏱️  Timeout - LLM is taking too long")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # 3. Check database
    print("\n3. Checking Database State:")
    try:
        response = requests.get(f"{base_url}/pending-actions/1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 Pending actions: {data.get('count', 0)}")
        else:
            print(f"   ❌ Failed to check pending actions")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    test()