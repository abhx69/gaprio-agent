"""
agent_brain.py - Fixed with proper response handling
"""

import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from database import db_manager
from tools.asana_tool import AsanaAPI
from tools.google_tool import send_gmail

load_dotenv()

class AgentBrain:
    """Main AI Agent brain with fixed database integration"""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv('LLM_MODEL', 'llama3:instruct')
        print(f"🧠 Initializing Agent Brain with model: {self.model}")
        self.llm = OllamaLLM(model=self.model, format="json")
        
        # Connect to database
        if not db_manager.connect():
            print("⚠️ Running in limited mode (no database connection)")
    
    def get_agent_plan(self, user_id: int, user_message: str) -> List[Dict]:
        """
        Generate action plan based on user message
        FIXED: Properly handles LLM response parsing
        """
        print(f"\n📨 Processing message from user {user_id}: {user_message}")
        
        # Get user's available tools
        asana_token = db_manager.get_user_token(user_id, 'asana')
        gmail_token = db_manager.get_user_token(user_id, 'google')
        
        has_asana = bool(asana_token)
        has_gmail = bool(gmail_token)
        
        print(f"   Available tools: Asana={has_asana}, Gmail={has_gmail}")
        
        # Build prompt
        prompt = self._build_planning_prompt(user_message, has_asana, has_gmail)
        
        try:
            print("🤖 Generating action plan with LLM...")
            response = self.llm.invoke(prompt)
            print(f"   LLM Raw Response: {response[:200]}...")
            
            # Parse response - handle different formats
            actions = self._parse_llm_response(response)
            
            # Save to pending actions table
            for action in actions:
                self._save_pending_action(user_id, action)
            
            print(f"✅ Generated {len(actions)} action(s)")
            return actions
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            print(f"   Raw response: {response}")
            return []
        except Exception as e:
            print(f"❌ Error in get_agent_plan: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_llm_response(self, response: str) -> List[Dict]:
        """Parse LLM response, handling different formats"""
        try:
            # Clean the response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
            
            # Parse JSON
            data = json.loads(response)
            
            # Handle different response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'actions' in data:
                    return data['actions']
                elif 'plan' in data:
                    return data['plan']
                elif 'tools' in data:
                    return data['tools']
                else:
                    # Try to extract any list from dict values
                    for value in data.values():
                        if isinstance(value, list):
                            return value
            return []
        except Exception as e:
            print(f"Warning: Could not parse response: {e}")
            return []
    
    def _build_planning_prompt(self, user_message: str, has_asana: bool, has_gmail: bool) -> str:
        """Build the LLM prompt for planning"""
        available_tools = []
        
        if has_asana:
            available_tools.append("- create_asana_task: Create a task in Asana (requires: name, notes, project_id)")
        
        if has_gmail:
            available_tools.append("- send_gmail: Send an email via Gmail (requires: to, subject, body)")
        
        tools_str = "\n".join(available_tools) if available_tools else "No tools available"
        
        return f"""
        You are Gaprio AI Assistant. Analyze the user's request and generate appropriate actions.
        
        USER REQUEST: "{user_message}"
        
        AVAILABLE TOOLS:
        {tools_str}
        
        INSTRUCTIONS:
        1. Only generate actions for available tools
        2. Extract parameters from the user's message
        3. For emails, extract recipient, subject, and body
        4. For tasks, extract task name and description
        5. For project_id, leave as empty string if not specified
        6. Output ONLY a JSON array of action objects
        7. DO NOT include any other text or explanations
        
        OUTPUT FORMAT: A JSON array like this:
        [
          {{
            "tool": "create_asana_task",
            "provider": "asana",
            "parameters": {{
              "name": "Task title here",
              "notes": "Task description here",
              "project_id": ""
            }}
          }}
        ]
        
        If no action is needed, return empty array: []
        
        Generate actions now:
        """
    
    def _save_pending_action(self, user_id: int, action: Dict) -> Optional[int]:
        """Save action to pending actions table"""
        try:
            # Extract action type
            tool = action.get('tool', '')
            provider = action.get('provider', '')
            
            # Map tool to action_type
            if tool == 'create_asana_task':
                action_type = 'create_task'
            elif tool == 'send_gmail':
                action_type = 'send_email'
            else:
                action_type = tool
            
            # Save to database
            return db_manager.create_pending_action(
                user_id=user_id,
                provider=provider,
                action_type=action_type,
                draft_payload=action
            )
        except Exception as e:
            print(f"Error saving pending action: {e}")
            return None
    
    def get_pending_actions(self, user_id: int) -> List[Dict]:
        """Get pending actions for a user"""
        return db_manager.get_pending_actions(user_id, 'pending')
    
    def approve_action(self, action_id: int) -> Dict:
        """Approve and execute a pending action"""
        try:
            print(f"⚡ Approving action {action_id}...")
            
            # Get action details
            actions = db_manager.get_pending_actions()
            action = next((a for a in actions if a['id'] == action_id), None)
            
            if not action:
                return {"success": False, "error": "Action not found"}
            
            user_id = action['user_id']
            provider = action['provider']
            draft_payload = action.get('draft_payload', {})
            
            print(f"   Action: {action.get('action_type')} for {provider}")
            
            # Get user token
            token_data = db_manager.get_user_token(user_id, provider)
            if not token_data:
                return {"success": False, "error": f"No {provider} token found"}
            
            # Execute action
            result = None
            if provider == 'asana' and draft_payload.get('tool') == 'create_asana_task':
                print("   Executing Asana task creation...")
                asana_api = AsanaAPI(token_data['access_token'])
                result = asana_api.create_task(draft_payload.get('parameters', {}))
            
            elif provider == 'google' and draft_payload.get('tool') == 'send_gmail':
                print("   Executing Gmail send...")
                from tools.google_tool import send_gmail
                result = send_gmail(token_data['access_token'], draft_payload.get('parameters', {}))
            
            # Update action status
            status = 'executed' if result and 'error' not in result else 'rejected'
            db_manager.update_action_status(action_id, status)
            
            return {
                "success": status == 'executed',
                "status": status,
                "result": result
            }
            
        except Exception as e:
            print(f"Error approving action: {e}")
            return {"success": False, "error": str(e)}

# Global instance
agent_brain = AgentBrain()

# Legacy function
def get_agent_plan(user_id: int, user_message: str) -> List[Dict]:
    """Legacy function for backward compatibility"""
    return agent_brain.get_agent_plan(user_id, user_message)