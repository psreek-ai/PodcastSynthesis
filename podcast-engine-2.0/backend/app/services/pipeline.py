import asyncio
import logging
import uuid
import os
import json
from .download import download_audio
from .transcribe import transcribe_audio
from app.ai.llm_router import PodcastCuratorLLM
from app.synthesis.cohost import AICoHost
from app.synthesis.advanced_media import advanced_stitch_with_crossfade
from app.db.database import add_feed_item

logging.basicConfig(level=logging.INFO)

async def process_podcast_task(url: str):
    """
    Background worker that handles the full ingestion and curation pipeline.
    """
    task_id = uuid.uuid4().hex[:8]
    logging.info(f"[Task {task_id}] Starting background job for URL: {url}")
    
    # Setup paths
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/feed", exist_ok=True)
    audio_path = f"data/raw/raw_{task_id}.mp3"
    
    try:
        # 1. Download Mode
        logging.info(f"[Task {task_id}] Downloading audio...")
        success = await asyncio.to_thread(download_audio, url, audio_path)
        if not success:
            logging.error(f"[Task {task_id}] Download failed.")
            return False
            
        # 2. Transcription
        logging.info(f"[Task {task_id}] Transcribing audio...")
        transcript = await asyncio.to_thread(transcribe_audio, audio_path)
        if not transcript or 'segments' not in transcript:
             logging.error(f"[Task {task_id}] Transcription failed.")
             return False
             
        # 3. LLM Analysis
        logging.info(f"[Task {task_id}] Analyzing concepts with LLM...")
        llm = PodcastCuratorLLM(use_local=False) # Switch to True if Ollama is running
        
        # Take the first 3 mins of transcript to mock knowledge extraction speed
        sample_chunk = json.dumps(transcript['segments'][:30]) 
        keep_segments = await asyncio.to_thread(llm.analyze_chunk, sample_chunk, "User knows general AI concepts.")
        
        if not keep_segments:
            logging.info(f"[Task {task_id}] No dense knowledge found to keep. Pipeline finished early.")
            return True
            
        # 4. Media Snipping (We will mock the actual FFmpeg slicing step here for brevity, 
        # and just stitch the raw audio with a TTS intro so the pipeline runs end-to-end)
        
        # 5. AI Co-Host Transition
        cohost = AICoHost(use_elevenlabs=True)
        intro_text = "Welcome to your infinite knowledge stream. Let's dive into this insight."
        logging.info(f"[Task {task_id}] Generating AI Co-Host TTS...")
        tts_audio = await asyncio.to_thread(cohost.generate_transition, intro_text)
        
        files_to_stitch = []
        if tts_audio and os.path.exists(tts_audio):
             files_to_stitch.append(tts_audio)
        
        # In a real run, we would append the individual sliced mp3 files here.
        # For testing the stitcher, we just append the raw downloaded audio.
        files_to_stitch.append(audio_path)
        
        # 6. Advanced Stitching
        final_output = f"data/feed/curated_{task_id}.mp3"
        logging.info(f"[Task {task_id}] Stitching audio with crossfades...")
        stitch_success = await asyncio.to_thread(advanced_stitch_with_crossfade, files_to_stitch, final_output)
        
        if not stitch_success:
             logging.error(f"[Task {task_id}] Failed to stitch media.")
             return False

        # 7. Database Entry
        logging.info(f"[Task {task_id}] Finalizing and saving to DB...")
        add_feed_item(
             item_id=f"seg_{task_id}",
             title="Extracted Insight: " + keep_segments[0].get('reasoning', 'Key Topic')[:30] + "...",
             source=url,
             audio_url=f"/media/curated_{task_id}.mp3",
             duration=120.5, # Mock duration
             tags=["AI", "Insight"],
             density="Ultra High"
        )
        
        logging.info(f"[Task {task_id}] Pipeline completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"[Task {task_id}] Pipeline execution error: {e}")
        return False
