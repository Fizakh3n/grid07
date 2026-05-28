# backend/main.py
# fastapi server that exposes grid07 phase2 as REST endpoints

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from phase2_content_engine import run_bot, BOT_PERSONAS

app = FastAPI(title="Grid07 API")

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# bot persona info for the UI
BOT_INFO = {
    "bot_a": {
        "name": "Alex Maximalist",
        "handle": "@techmaxi_alex",
        "avatar": "A",
        "color": "#00ff9d",
        "tag": "Tech Maximalist",
        "bio": "AI + crypto will save humanity. Regulations are for losers.",
    },
    "bot_b": {
        "name": "Blake Doomer",
        "handle": "@doomscroll_blake",
        "avatar": "B",
        "color": "#ff4d6d",
        "tag": "Skeptic / Doomer",
        "bio": "Big tech is eating society alive. Wake up people.",
    },
    "bot_c": {
        "name": "Chase Finance",
        "handle": "@chase_roi",
        "avatar": "C",
        "color": "#ffd60a",
        "tag": "Finance Bro",
        "bio": "Everything is ROI. Markets never lie. Money talks.",
    },
}

class GenerateRequest(BaseModel):
    bot_id: str

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/api/bots")
def get_bots():
    # returns all bot info for the frontend cards
    return {"bots": BOT_INFO}

@app.post("/api/generate")
def generate_post(req: GenerateRequest):
    # validates bot_id then runs the langgraph pipeline
    if req.bot_id not in BOT_PERSONAS:
        raise HTTPException(status_code=400, detail="invalid bot_id")
    try:
        result = run_bot(req.bot_id)
        result["bot_info"] = BOT_INFO[req.bot_id]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
