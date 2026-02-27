import base64
import json
import logging
import os
import secrets
import urllib.parse
import webbrowser

import httpx
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO)

auth_router = APIRouter()

# --- Anthropic Claude Code OAuth Credentials ---
# These are the public Claude Code / Claude.ai OAuth client credentials.
# They are NOT secret — they are the same ones used by the official Claude Code CLI.
ANTHROPIC_CLIENT_ID = "9d1c250a-d61e-4469-80ed-5944d196f5a0"
ANTHROPIC_AUTHORIZE_URL = "https://claude.ai/oauth/authorize"
ANTHROPIC_TOKEN_URL = "https://claude.ai/oauth/token"
REDIRECT_URI = "http://localhost:8000/auth/anthropic/callback"
SCOPES = "org:create_api_key user:profile user:inference"

CONFIG_FILE = "data/config.json"

# Temporary store for the state nonce during OAuth
_oauth_state = {}


@auth_router.get("/auth/anthropic/start")
def start_anthropic_auth():
    """
    Step 1: Generates the OAuth URL and opens the browser for the user to log in.
    The user just clicks 'Authorize' — no token copy-pasting required.
    """
    state = secrets.token_urlsafe(16)
    _oauth_state["state"] = state

    params = {
        "response_type": "code",
        "client_id": ANTHROPIC_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge_method": "S256",
        # Note: In a full PKCE flow, we'd generate a code_verifier here.
        # For now, we skip PKCE as the public client flow accepts it.
    }

    auth_url = f"{ANTHROPIC_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    logging.info(f"Opening Anthropic auth URL: {auth_url}")

    # Open browser on the SERVER side (the machine running the backend)
    webbrowser.open(auth_url)

    return {
        "status": "browser_opened",
        "message": "Opened Anthropic login in your browser. Authorize to complete setup.",
    }


@auth_router.get("/auth/anthropic/callback", response_class=HTMLResponse)
async def anthropic_callback(code: str, state: str):
    """
    Step 2: Anthropic redirects back here after the user clicks 'Authorize'.
    We exchange the authorization code for an access token automatically.
    """

    if state != _oauth_state.get("state"):
        return HTMLResponse(
            "<h1 style='font-family:sans-serif; color:red'>Security Error: State mismatch. Please try again.</h1>",
            status_code=400,
        )

    # Exchange code for token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ANTHROPIC_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": ANTHROPIC_CLIENT_ID,
                },
            )

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            logging.error(f"Token exchange failed: {token_data}")
            return HTMLResponse(
                f"<h1 style='font-family:sans-serif;color:red'>Auth failed. Check backend logs.</h1><pre>{json.dumps(token_data, indent=2)}</pre>",
                status_code=400,
            )

        # Persist the token to environment and config file
        os.environ["ANTHROPIC_API_KEY"] = access_token
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        current_config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    current_config = json.load(f)
            except Exception:
                pass

        current_config["claude_token"] = access_token
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f)

        logging.info("Anthropic OAuth token obtained and saved successfully.")

        # Show a beautiful success page that auto-closes
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Engine.ai — Connected</title>
  <style>
    body {
      background: #050505; color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;
    }
    .card {
      text-align: center; padding: 60px; border: 1px solid rgba(255,255,255,0.08);
      border-radius: 32px; background: rgba(255,255,255,0.04); max-width: 400px;
    }
    .icon { font-size: 56px; margin-bottom: 16px; }
    h1 { font-size: 28px; font-weight: 800; margin: 0 0 8px; }
    p { color: rgba(255,255,255,0.5); font-size: 16px; }
    .pill {
      display: inline-block; margin-top: 20px; padding: 8px 20px; border-radius: 100px;
      background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
      color: #818cf8; font-size: 14px; font-weight: 600;
    }
  </style>
  <script>setTimeout(() => window.close(), 3000);</script>
</head>
<body>
  <div class="card">
    <div class="icon">✅</div>
    <h1>Connected!</h1>
    <p>Claude is now authenticated.<br>This window will close automatically.</p>
    <div class="pill">Engine.ai is now powered by Claude</div>
  </div>
</body>
</html>
""")

    except Exception as e:
        logging.error(f"OAuth callback error: {e}")
        return HTMLResponse(f"<h1 style='color:red'>Error: {e}</h1>", status_code=500)


# ---------------------------------------------------------------------------
# Spotify OAuth — inspired by PodcastKnowledgeDistiller's Spotify integration
# Lets users browse their saved podcast shows directly inside the app.
# ---------------------------------------------------------------------------

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_REDIRECT_URI = "http://localhost:8000/auth/spotify/callback"
SPOTIFY_SCOPES = "user-library-read user-follow-read"

_spotify_oauth_state: dict = {}


@auth_router.get("/auth/spotify/start")
def start_spotify_auth():
    """
    Step 1: Generates the Spotify OAuth URL and opens the browser.
    Requires SPOTIPY_CLIENT_ID env var.
    """
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    if not client_id:
        return JSONResponse(
            {"error": "SPOTIPY_CLIENT_ID not set. Add it to your .env file."},
            status_code=400,
        )

    state = secrets.token_urlsafe(16)
    _spotify_oauth_state["state"] = state

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
    }

    auth_url = f"{SPOTIFY_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    logging.info(f"Opening Spotify auth URL: {auth_url}")
    webbrowser.open(auth_url)

    return {
        "status": "browser_opened",
        "message": "Opened Spotify login in your browser. Authorize to connect your podcast library.",
    }


@auth_router.get("/auth/spotify/callback", response_class=HTMLResponse)
async def spotify_callback(code: str, state: str):
    """
    Step 2: Spotify redirects here after the user clicks 'Agree'.
    Exchanges the authorization code for tokens and saves them.
    """
    if state != _spotify_oauth_state.get("state"):
        return HTMLResponse(
            "<h1 style='font-family:sans-serif;color:red'>Security Error: State mismatch. Please try again.</h1>",
            status_code=400,
        )

    client_id = os.getenv("SPOTIPY_CLIENT_ID", "")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "")
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPOTIFY_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": SPOTIFY_REDIRECT_URI,
                },
            )

        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            return HTMLResponse(
                f"<h1 style='color:red'>Spotify auth failed.</h1><pre>{json.dumps(token_data, indent=2)}</pre>",
                status_code=400,
            )

        os.environ["SPOTIFY_ACCESS_TOKEN"] = access_token
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        current_config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    current_config = json.load(f)
            except Exception:
                pass

        current_config["spotify_access_token"] = access_token
        if refresh_token:
            current_config["spotify_refresh_token"] = refresh_token
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f)

        logging.info("Spotify OAuth token obtained and saved.")

        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Engine.ai — Spotify Connected</title>
  <style>
    body {
      background: #050505; color: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;
    }
    .card {
      text-align: center; padding: 60px; border: 1px solid rgba(255,255,255,0.08);
      border-radius: 32px; background: rgba(255,255,255,0.04); max-width: 400px;
    }
    .icon { font-size: 56px; margin-bottom: 16px; }
    h1 { font-size: 28px; font-weight: 800; margin: 0 0 8px; }
    p { color: rgba(255,255,255,0.5); font-size: 16px; }
    .pill {
      display: inline-block; margin-top: 20px; padding: 8px 20px; border-radius: 100px;
      background: rgba(29,185,84,0.15); border: 1px solid rgba(29,185,84,0.3);
      color: #1db954; font-size: 14px; font-weight: 600;
    }
  </style>
  <script>setTimeout(() => window.close(), 3000);</script>
</head>
<body>
  <div class="card">
    <div class="icon">🎧</div>
    <h1>Spotify Connected!</h1>
    <p>Your podcast library is now available.<br>This window will close automatically.</p>
    <div class="pill">Engine.ai can now browse your shows</div>
  </div>
</body>
</html>
""")

    except Exception as e:
        logging.error(f"Spotify OAuth callback error: {e}")
        return HTMLResponse(f"<h1 style='color:red'>Error: {e}</h1>", status_code=500)


@auth_router.get("/api/spotify/shows")
async def get_spotify_shows(limit: int = 20):
    """
    Returns the user's followed/saved Spotify podcast shows.
    Requires a valid Spotify access token (obtained via /auth/spotify/start).
    """
    access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")

    # Also try loading from config file on startup
    if not access_token and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            access_token = cfg.get("spotify_access_token")
            if access_token:
                os.environ["SPOTIFY_ACCESS_TOKEN"] = access_token
        except Exception:
            pass

    if not access_token:
        return JSONResponse(
            {"error": "Not connected to Spotify. Visit /auth/spotify/start to authorize."},
            status_code=401,
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.spotify.com/v1/me/shows",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit},
            )

        if response.status_code == 401:
            return JSONResponse(
                {"error": "Spotify token expired. Re-authorize at /auth/spotify/start."},
                status_code=401,
            )

        data = response.json()
        shows = [
            {
                "id": item["show"]["id"],
                "name": item["show"]["name"],
                "publisher": item["show"]["publisher"],
                "description": item["show"]["description"][:200],
                "image": item["show"]["images"][0]["url"] if item["show"]["images"] else None,
                "episodes_total": item["show"]["total_episodes"],
            }
            for item in data.get("items", [])
        ]
        return {"shows": shows, "total": len(shows)}

    except Exception as e:
        logging.error(f"Error fetching Spotify shows: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
