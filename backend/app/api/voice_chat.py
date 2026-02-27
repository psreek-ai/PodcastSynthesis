import logging

from fastapi import APIRouter
from litellm import completion
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

# Router for the interactive voice features
chat_router = APIRouter()


class VoiceInterruptRequest(BaseModel):
    user_query_text: str
    current_podcast_context: str


@chat_router.post("/api/chat/interrupt")
def handle_voice_interrupt(request: VoiceInterruptRequest):
    """
    Handles the "Hold Spacebar to Ask" feature.
    Takes the user's transcribed question and the recent 2 minutes of podcast transcript.
    Returns the AI's answer, which the frontend will TTS and play.
    """
    logging.info(f"Voice interruption received: {request.user_query_text}")

    prompt = f"""You are the AI Co-Host of a podcast. The user just interrupted the stream to ask a question about what the speakers were just discussing.

Recent Podcast Context:
{request.current_podcast_context}

User's Question:
{request.user_query_text}

Answer the user directly, conversationally, and concisely (1-3 sentences max).
"""

    try:
        response = completion(
            model="anthropic/claude-3-haiku-20240307",  # Fast response critical for voice chat
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        answer = response.choices[0].message.content
        return {"status": "success", "answer_text": answer}

    except Exception as e:
        logging.error(f"Voice interrupt LLM error: {e}")
        return {"status": "error", "message": "Could not connect to AI."}


# To use this in main.py:
# from app.api.voice_chat import chat_router
# app.include_router(chat_router)
