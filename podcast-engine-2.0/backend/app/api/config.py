from pydantic import BaseModel
from fastapi import APIRouter
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

config_router = APIRouter()

class ConfigUpdate(BaseModel):
    claude_token: str | None = None
    spotify_client_id: str | None = None
    spotify_client_secret: str | None = None
    elevenlabs_api_key: str | None = None

CONFIG_FILE = "data/config.json"

@config_router.post("/api/config")
def update_config(config: ConfigUpdate):
    """
    Updates the environment variables dynamically for the current session,
    and saves them to a local config so they persist across restarts.
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    current_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                current_config = json.load(f)
        except Exception:
            pass
            
    # Update values
    if config.claude_token:
        os.environ["ANTHROPIC_API_KEY"] = config.claude_token
        current_config["claude_token"] = config.claude_token
        
    if config.spotify_client_id:
        os.environ["SPOTIPY_CLIENT_ID"] = config.spotify_client_id
        current_config["spotify_client_id"] = config.spotify_client_id
        
    if config.spotify_client_secret:
        os.environ["SPOTIPY_CLIENT_SECRET"] = config.spotify_client_secret
        current_config["spotify_client_secret"] = config.spotify_client_secret
        
    if config.elevenlabs_api_key:
        os.environ["ELEVENLABS_API_KEY"] = config.elevenlabs_api_key
        current_config["elevenlabs_api_key"] = config.elevenlabs_api_key
        
    with open(CONFIG_FILE, "w") as f:
        json.dump(current_config, f)
        
    logging.info("Configuration updated successfully.")
    return {"status": "success", "message": "API Keys saved and applied."}
    
@config_router.get("/api/config")
def get_config():
    """Returns whether keys are set (without returning the actual secret keys)."""
    return {
        "has_claude": "ANTHROPIC_API_KEY" in os.environ or os.environ.get("ANTHROPIC_API_KEY"),
        "has_spotify": "SPOTIPY_CLIENT_ID" in os.environ or os.environ.get("SPOTIPY_CLIENT_ID"),
        "has_elevenlabs": "ELEVENLABS_API_KEY" in os.environ or os.environ.get("ELEVENLABS_API_KEY"),
    }
