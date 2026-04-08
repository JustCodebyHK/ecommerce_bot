import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# 1. Path Management: Ensure models.py is findable
# We look one level up from the /server folder
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

try:
    from models import Action, Observation
    from .ecommerce_bot_environment import EcommerceBotEnvironment
except ImportError as e:
    print(f"CRITICAL ERROR: Missing modules. Check your folder structure. {e}")
    sys.exit(1)

# 2. Initialize FastAPI
app = FastAPI(
    title="Meta x Scalar: OpenEnv Ecommerce Bot",
    description="Agentic System for Real-World E-commerce Automation",
    version="1.0.0"
)

# 3. Add CORS (Allows the Hugging Face UI to talk to your API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Initialize the Environment
# This triggers the SQLite connection in your EcommerceBotEnvironment class
env = EcommerceBotEnvironment()

# --- ROUTES ---

@app.get("/")
async def root():
    """Entry point for Hugging Face Spaces UI."""
    return {
        "message": "E-commerce Bot API is running",
        "status": "online",
        "spec": "OpenEnv v1.0",
        "university": "Mumbai University Campus"
    }

@app.get("/health")
async def health():
    """
    DOCKER HEALTHCHECK: 
    Matches the 'CMD curl' in your Dockerfile to ensure container status is 'Healthy'.
    """
    return {"status": "healthy", "database": "connected"}

@app.get("/state")
async def get_state():
    """
    MANDATORY OPENENV ENDPOINT:
    Used by 'openenv validate' to check readiness before testing starts.
    """
    return {
        "status": "ready", 
        "tasks": ["create_order", "update_address", "issue_refund"],
        "persistance": "sqlite3"
    }

@app.post("/reset")
async def reset():
    """
    Standard OpenEnv Reset.
    Clears local memory (but keeps the SQLite DB persistent).
    """
    observation = env.reset()
    return observation

@app.post("/step")
async def step(action: Action):
    """
    Standard OpenEnv Step.
    Returns the mandatory 4-part tuple (obs, reward, done, info).
    """
    # Unpack the environment logic
    observation, reward, done, info = env.step(action)
    
    # Cast values to ensure JSON compatibility for the grader
    return {
        "observation": observation,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

# 5. Clean Shutdown
@app.on_event("shutdown")
def shutdown_event():
    """Closes connections when the container stops."""
    print("Shutting down E-commerce Bot Server...")

# 6. Local Debugging Support
if __name__ == "__main__":
    import uvicorn
    # Use environment port if available (for HF Spaces), otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)