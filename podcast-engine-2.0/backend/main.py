from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import logging
import os
from contextlib import asynccontextmanager

from app.db.database import init_db, get_feed
from app.services.pipeline import process_podcast_task
from app.api.config import config_router
from app.api.voice_chat import chat_router
from app.api.auth import auth_router

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database on startup
    init_db()
    yield
    # Cleanup on shutdown

app = FastAPI(title="AI Podcast Engine 2.0 API", version="2.0.0", lifespan=lifespan)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/feed", exist_ok=True)
app.mount("/media", StaticFiles(directory="data/feed"), name="media")

app.include_router(config_router)
app.include_router(chat_router)
app.include_router(auth_router)

class PodcastProcessRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Podcast Engine 2.0"}

@app.post("/api/process")
async def process_podcast(request: PodcastProcessRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to trigger the asynchronous podcast processing pipeline.
    """
    url = request.url
    # Add to background queue to prevent API blocking
    background_tasks.add_task(process_podcast_task, url)
    return {"status": "processing_started", "url": url, "message": "Podcast added to processing queue."}

@app.get("/api/feed")
def get_user_feed():
    """
    Retrieves the chronological 'Infinite Knowledge' feed from the database.
    """
    items = get_feed(limit=20)
    
    # If the database is empty, return initial mock data so the frontend renders beautifully
    if not items:
        return {
            "feed": [
                {
                    "id": "mock_1",
                    "title": "Lex Fridman on AGI Timelines",
                    "source": "Lex Fridman Podcast #333",
                    "audio_url": "", 
                    "duration": 105.0,
                    "tags": ["AGI", "Future", "Machine Learning"],
                    "knowledge_density": "Ultra High"
                },
                {
                    "id": "mock_2",
                    "title": "Huberman on High Performance Focus",
                    "source": "Huberman Lab",
                    "audio_url": "",
                    "duration": 60.0,
                    "tags": ["Neuroscience", "Focus", "Health"],
                    "knowledge_density": "High"
                }
            ]
        }
    
    return {"feed": items}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
