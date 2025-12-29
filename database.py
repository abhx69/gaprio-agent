"""
database.py - Fixed database connection with proper cursor handling
"""

import os
import mysql.connector
from datetime import datetime
from typing import Dict, Optional, List, Any
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

class DatabaseManager:
    """Handles database connections and operations with proper cursor management"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'Axkpq@8210'),
            'database': os.getenv('DB_NAME', 'gaprio_agent_dev'),
            'raise_on_warnings': True,
            'buffered': True,  # Important for preventing "unread result found"
            'autocommit': True  # Auto-commit transactions
        }
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection with buffered cursor"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            
            # Test connection with buffered cursor
            cursor = self.connection.cursor(buffered=True)
            cursor.execute("SELECT 1")
            cursor.fetchall()  # Read all results
            cursor.close()
            
            print(f"✅ Connected to database: {self.config['database']}")
            return True
        except Error as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
    
    def get_user_token(self, user_id: int, provider: str) -> Optional[Dict]:
        """Get OAuth token for a user and provider with buffered cursor"""
        try:
            cursor = self.connection.cursor(buffered=True, dictionary=True)
            query = """
                SELECT access_token, refresh_token, expires_at 
                FROM user_connections 
                WHERE user_id = %s AND provider = %s
                ORDER BY updated_at DESC 
                LIMIT 1
            """
            cursor.execute(query, (user_id, provider))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                # Check if token is expired
                if result['expires_at'] and result['expires_at'] < datetime.now():
                    print(f"⚠️ Token expired for user {user_id}, provider {provider}")
                    return None
                return result
            return None
            
        except Error as e:
            print(f"Error fetching token: {e}")
            return None
    
    def save_chat_message(self, user_id: int, role: str, content: str) -> Optional[int]:
        """Save a chat message to maintain context/memory"""
        try:
            cursor = self.connection.cursor(buffered=True)
            query = """
                INSERT INTO agent_chat_logs (user_id, role, content)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, role, content))
            self.connection.commit()
            message_id = cursor.lastrowid
            cursor.close()
            print(f"💾 Saved chat message: {role} - {content[:50]}...")
            return message_id
        except Error as e:
            print(f"Error saving chat message: {e}")
            return None
    
    def create_pending_action(self, user_id: int, provider: str, 
                            action_type: str, draft_payload: Dict) -> Optional[int]:
        """Create a draft action waiting for user approval"""
        try:
            import json
            cursor = self.connection.cursor(buffered=True)
            query = """
                INSERT INTO ai_pending_actions 
                (user_id, provider, action_type, draft_payload, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """
            cursor.execute(query, (user_id, provider, action_type, 
                                 json.dumps(draft_payload)))
            self.connection.commit()
            action_id = cursor.lastrowid
            cursor.close()
            print(f"📝 Created pending action {action_id}: {action_type}")
            return action_id
        except Error as e:
            print(f"Error creating pending action: {e}")
            return None
    
    def get_pending_actions(self, user_id: Optional[int] = None, 
                           status: str = 'pending') -> List[Dict]:
        """Get pending actions awaiting approval"""
        try:
            cursor = self.connection.cursor(buffered=True, dictionary=True)
            
            if user_id:
                query = """
                    SELECT id, user_id, provider, action_type, draft_payload, created_at
                    FROM ai_pending_actions
                    WHERE user_id = %s AND status = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (user_id, status))
            else:
                query = """
                    SELECT id, user_id, provider, action_type, draft_payload, created_at
                    FROM ai_pending_actions
                    WHERE status = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (status,))
            
            actions = cursor.fetchall()
            
            # Parse JSON payload
            import json
            for action in actions:
                if 'draft_payload' in action and action['draft_payload']:
                    try:
                        action['draft_payload'] = json.loads(action['draft_payload'])
                    except:
                        action['draft_payload'] = {}
            
            cursor.close()
            return actions
        except Error as e:
            print(f"Error fetching pending actions: {e}")
            return []
    
    def update_action_status(self, action_id: int, 
                           status: str, executed_data: Optional[Dict] = None):
        """Update status of a pending action"""
        try:
            cursor = self.connection.cursor(buffered=True)
            
            if status == 'executed':
                query = """
                    UPDATE ai_pending_actions 
                    SET status = %s, executed_at = NOW()
                    WHERE id = %s
                """
            else:
                query = """
                    UPDATE ai_pending_actions 
                    SET status = %s
                    WHERE id = %s
                """
            
            cursor.execute(query, (status, action_id))
            self.connection.commit()
            cursor.close()
            print(f"🔄 Updated action {action_id} status to: {status}")
            return True
        except Error as e:
            print(f"Error updating action status: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute a generic query with buffered cursor"""
        try:
            cursor = self.connection.cursor(buffered=True, dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
        except Error as e:
            print(f"Query execution error: {e}")
            return None

# Global instance
db_manager = DatabaseManager()

def get_user_token(user_id: int, provider: str) -> Optional[str]:
    """Legacy function for backward compatibility"""
    result = db_manager.get_user_token(user_id, provider)
    return result['access_token'] if result else None