"""
test_fixed.py - Fixed test script
"""

import requests
import json
import time

def test_system():
    print("🧪 Testing Fixed System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Health check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health = response.json()
        print(f"   Status: {health.get('status')}")
        print(f"   Database: {health.get('database')}")
        print(f"   Ollama: {health.get('ollama')}")
        
        if health.get('database') != 'connected':
            print("   ⚠️  Database is disconnected!")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # 2. Test ask-agent
    print("\n2. Testing Ask Agent...")
    test_cases = [
        {"message": "Create a task to review website design", "expected_tool": "create_asana_task"},
        {"message": "Send email to team@example.com about the project update", "expected_tool": "send_gmail"},
        {"message": "What time is it?", "expected_actions": 0}
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n   Test {i}: '{test['message']}'")
        
        try:
            response = requests.post(
                f"{base_url}/ask-agent",
                json={"user_id": 1, "message": test['message']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     Status: {result.get('status')}")
                print(f"     Message: {result.get('message')}")
                
                plan = result.get('plan', [])
                if isinstance(plan, list):
                    print(f"     Actions: {len(plan)}")
                    for j, action in enumerate(plan, 1):
                        print(f"       {j}. {action.get('tool', 'unknown')}")
                        
                        # Check if action has expected tool
                        if 'expected_tool' in test and action.get('tool') == test['expected_tool']:
                            print(f"         ✅ Correct tool detected")
                
                # Save for inspection
                with open(f'test_response_{i}.json', 'w') as f:
                    json.dump(result, f, indent=2)
                
            else:
                print(f"     ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # 3. Check pending actions
    print("\n3. Checking Pending Actions...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/pending-actions/1", timeout=5)
        if response.status_code == 200:
            result = response.json()
            count = result.get('count', 0)
            print(f"   Found {count} pending actions")
            
            if count > 0:
                actions = result.get('actions', [])
                for i, action in enumerate(actions, 1):
                    print(f"     {i}. ID: {action.get('id')} - {action.get('action_type')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    return True

if __name__ == "__main__":
    test_system()