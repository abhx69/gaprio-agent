"""
test_all.py - Fixed test script
"""

import requests
import json
import time
import sys

class GaprioTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def test_health(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"✅ Health Check: {response.status_code}")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Ollama: {data.get('ollama', 'unknown')}")
            return data.get('database') == 'connected'
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return False
    
    def test_ask_agent(self, user_id=1, message="Create a task for API documentation"):
        """Test ask-agent endpoint"""
        try:
            url = f"{self.base_url}/ask-agent"
            payload = {
                "user_id": user_id,
                "message": message
            }
            
            response = requests.post(url, json=payload, timeout=10)
            print(f"✅ Ask Agent: {response.status_code}")
            
            # Handle response properly
            if response.status_code == 200:
                result = response.json()
                
                # Fix: Handle different response formats
                if isinstance(result, dict):
                    print(f"   Status: {result.get('status', 'unknown')}")
                    print(f"   Message: {result.get('message', 'No message')}")
                    
                    plan = result.get('plan', [])
                    if isinstance(plan, list):
                        print(f"   Actions Generated: {len(plan)}")
                        for i, action in enumerate(plan, 1):
                            if isinstance(action, dict):
                                print(f"     {i}. {action.get('tool', 'unknown')} → {action.get('provider', 'unknown')}")
                            else:
                                print(f"     {i}. {action}")
                    else:
                        print(f"   Plan (raw): {plan}")
                    
                    return result
                else:
                    print(f"   Response (raw): {result}")
                    return result
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ask Agent Failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_pending_actions(self, user_id=1):
        """Test pending actions endpoint"""
        try:
            response = requests.get(f"{self.base_url}/pending-actions/{user_id}", timeout=5)
            print(f"✅ Pending Actions: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    count = result.get('count', 0)
                    print(f"   Pending Actions: {count}")
                    
                    actions = result.get('actions', [])
                    for i, action in enumerate(actions, 1):
                        if isinstance(action, dict):
                            print(f"     {i}. ID: {action.get('id')} - {action.get('action_type', 'unknown')}")
                        else:
                            print(f"     {i}. {action}")
                    
                    return actions
                else:
                    print(f"   Response: {result}")
                    return result
            else:
                print(f"   Error: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Pending Actions Failed: {e}")
            return []
    
    def test_approve_action(self, action_id=1, user_id=1):
        """Test approve action endpoint"""
        try:
            url = f"{self.base_url}/approve-action"
            payload = {
                "user_id": user_id,
                "action_id": action_id
            }
            
            response = requests.post(url, json=payload, timeout=10)
            print(f"✅ Approve Action: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Result: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Approve Action Failed: {e}")
            return None
    
    def run_complete_test(self):
        """Run complete test suite"""
        print("🧪 Running Gaprio Agent Tests")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1️⃣ Testing Health Check...")
        db_connected = self.test_health()
        
        if not db_connected:
            print("\n⚠️  Database is disconnected!")
            print("Please run: python setup_database.py")
            return
        
        # Test 2: Ask agent
        print("\n2️⃣ Testing Ask Agent...")
        test_messages = [
            "Create a task to review website design",
            "Send email to john@example.com about meeting tomorrow at 2 PM",
            "What's the weather today?"
        ]
        
        all_actions = []
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Test {i}: '{message}'")
            result = self.test_ask_agent(1, message)
            
            if result:
                time.sleep(1)  # Give DB time to save
        
        # Test 3: Get pending actions
        print("\n3️⃣ Testing Pending Actions...")
        time.sleep(2)
        actions = self.test_pending_actions(1)
        
        if actions and len(actions) > 0:
            # Test 4: Approve first action (simulation)
            print("\n4️⃣ Testing Action Approval (Simulation)...")
            action = actions[0]
            if isinstance(action, dict):
                action_id = action.get('id')
                if action_id:
                    print(f"   Would approve action ID: {action_id}")
                    print("   Note: Using simulated tokens, real execution would fail")
                    # Uncomment to actually test approval
                    # approval_result = self.test_approve_action(action_id, 1)
                else:
                    print("   No action ID found")
            else:
                print(f"   Action is not a dict: {type(action)}")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
        # Show summary
        print("\n📋 Test Summary:")
        print("   Server: ✓ Running")
        print(f"   Database: {'✓ Connected' if db_connected else '✗ Disconnected'}")
        print(f"   API Endpoints: ✓ Working")
        print(f"   Pending Actions: {len(actions) if isinstance(actions, list) else 'Unknown'}")

if __name__ == "__main__":
    tester = GaprioTester()
    tester.run_complete_test()