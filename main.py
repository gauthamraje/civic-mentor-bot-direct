import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Socratic civic Mentor API")

# Enable CORS for all origins (especially useful for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# MODELS
# -----------------------------------------------------------------------------
class ChatMessage(BaseModel):
    content: str

class ThreadResponse(BaseModel):
    thread_id: str

class RunResponse(BaseModel):
    thread_id: str
    run_id: str

# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/threads", response_model=ThreadResponse)
def create_thread():
    """Create a new session (Thread) for a student."""
    try:
        thread = client.beta.threads.create()
        return {"thread_id": thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/threads/{thread_id}/messages", response_model=RunResponse)
def post_message(thread_id: str, msg: ChatMessage):
    """Post a message to a thread and trigger an Assistant run."""
    try:
        # Add the message
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=msg.content
        )
        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        return {"thread_id": thread_id, "run_id": run.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}/runs/{run_id}")
def check_run_status(thread_id: str, run_id: str):
    """Poll for the completion of a run."""
    try:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        return {"status": run.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}/messages")
def get_messages(thread_id: str):
    """Fetch all messages from the thread (used when run is 'completed')."""
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return {"messages": [
            {
                "role": m.role,
                "content": m.content[0].text.value if m.content else ""
            } for m in messages.data
        ][::-1]} # Reverse to get chronological order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# FRONTEND SERVING
# -----------------------------------------------------------------------------
# Note: Static files should be in the 'static' directory
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    print("Warning: Static directory not found. Skipping static mount.")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serves the main mobile-fist UI."""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Project Initialized.</h1><p>Static index.html not yet created.</p>"
