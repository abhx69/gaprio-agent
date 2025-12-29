"""
main.py - FastAPI application
"""

import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent_brain import agent_brain, get_agent_plan
from database import db_manager  # Add this import
from tools.asana_tool import execute_asana_task
from tools.google_tool import send_gmail

load_dotenv()

app = FastAPI(title="Gaprio Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserMessage(BaseModel):
    user_id: int
    message: str

class ActionApproval(BaseModel):
    user_id: int
    action_id: int

class ActionData(BaseModel):
    tool: str
    provider: str
    parameters: Dict

# Routes
@app.get("/")
async def root():
    return {"message": "Gaprio Agent API", "status": "running"}

@app.post("/ask-agent", response_model=Dict)
async def ask_agent(user_msg: UserMessage):
    """
    Process user message and generate action plan
    """
    try:
        plan = get_agent_plan(user_msg.user_id, user_msg.message)
        
        return {
            "status": "success",
            "plan": plan,
            "requires_approval": len(plan) > 0,
            "message": f"Generated {len(plan)} action(s) pending approval"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pending-actions/{user_id}", response_model=Dict)
async def get_pending_actions(user_id: int):
    """
    Get all pending actions for a user
    """
    try:
        actions = agent_brain.get_pending_actions(user_id)
        
        return {
            "status": "success",
            "count": len(actions),
            "actions": actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve-action", response_model=Dict)
async def approve_action(approval: ActionApproval):
    """
    Approve and execute a pending action
    """
    try:
        result = agent_brain.approve_action(approval.action_id)
        
        if result["success"]:
            return {
                "status": "success",
                "message": "Action executed successfully",
                "data": result.get("result")
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Execution failed")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-action", response_model=Dict)
async def execute_action(action: ActionData):
    """
    Direct action execution (without approval flow)
    """
    try:
        token = db_manager.get_user_token(action.user_id, action.provider)
        
        if not token:
            raise HTTPException(status_code=400, detail=f"No {action.provider} token found")
        
        result = None
        if action.provider == 'asana' and action.tool == 'create_asana_task':
            result = execute_asana_task(token, action.parameters)
        elif action.provider == 'google' and action.tool == 'send_gmail':
            result = send_gmail(token, action.parameters)
        else:
            raise HTTPException(status_code=400, detail="Unsupported action")
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint with proper database connection test"""
    try:
        # Test database connection
        db_status = "disconnected"
        try:
            # Use db_manager instance
            if db_manager.connection and db_manager.connection.is_connected():
                # Test with a simple query
                cursor = db_manager.connection.cursor(buffered=True)
                cursor.execute("SELECT 1")
                cursor.fetchall()
                cursor.close()
                db_status = "connected"
        except Exception as e:
            print(f"Database health check error: {e}")
            db_status = "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "ollama": "configured",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('APP_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)