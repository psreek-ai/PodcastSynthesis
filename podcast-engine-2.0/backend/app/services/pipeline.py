"""
Main orchestration pipeline for the AI Podcast Engine.

Takes a URL through the full ingestion flow:
  download -> transcribe -> LLM analysis -> knowledge graph filter
  -> AI Co-Host -> stitch -> feed DB -> update knowledge graph
"""

import asyncio
import json
import logging
import os
import uuid

from app.ai.llm_router import PodcastCuratorLLM
from app.core.knowledge_graph import KnowledgeGraph
from app.db.database import add_feed_item
from app.synthesis.advanced_media import advanced_stitch_with_crossfade
from app.synthesis.cohost import AICoHost

from .download import download_audio
from .transcribe import transcribe_audio

logger = logging.getLogger(__name__)


async def process_podcast_task(url: str) -> bool:
    """
    Background worker that handles the full ingestion and curation pipeline.

    Steps:
    1. Download audio via yt-dlp
    2. Transcribe with Whisper (word-level timestamps)
    3. Analyze with LLM to identify high-density segments
    4. Filter segments against the user's Knowledge Graph (skip known concepts)
    5. Generate AI Co-Host transition audio via ElevenLabs
    6. Stitch clips with FFmpeg crossfades
    7. Save curated item to feed database
    8. Update Knowledge Graph with newly learned concepts

    Returns True on success, False on failure.
    """
    task_id = uuid.uuid4().hex[:8]
    logger.info(f"[Task {task_id}] Starting pipeline for URL: {url}")

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/feed", exist_ok=True)
    raw_audio_path = f"data/raw/raw_{task_id}.mp3"

    try:
        # Step 1: Download
        logger.info(f"[Task {task_id}] Step 1/7 - Downloading audio...")
        success = await asyncio.to_thread(download_audio, url, raw_audio_path)
        if not success:
            logger.error(f"[Task {task_id}] Download failed. Aborting.")
            return False

        # Step 2: Transcribe
        logger.info(f"[Task {task_id}] Step 2/7 - Transcribing with Whisper...")
        transcript = await asyncio.to_thread(transcribe_audio, raw_audio_path)
        if not transcript or not transcript.get("segments"):
            logger.error(f"[Task {task_id}] Transcription returned no segments. Aborting.")
            return False

        # Step 3: LLM Analysis
        logger.info(f"[Task {task_id}] Step 3/7 - Analyzing with LLM...")
        use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        llm = PodcastCuratorLLM(use_local=use_local)

        all_segments = transcript["segments"]
        chunk_size = 30
        keep_segments = []

        for chunk_start in range(0, min(len(all_segments), 90), chunk_size):
            chunk = all_segments[chunk_start : chunk_start + chunk_size]
            result = await asyncio.to_thread(llm.analyze_chunk, json.dumps(chunk), "")
            if result:
                keep_segments.extend(result)

        if not keep_segments:
            logger.info(f"[Task {task_id}] LLM found no high-density segments. Skipping.")
            return True

        logger.info(f"[Task {task_id}] LLM identified {len(keep_segments)} valuable segments.")

        # Step 4: Knowledge Graph Deduplication
        logger.info(f"[Task {task_id}] Step 4/7 - Filtering against knowledge graph...")
        kg = KnowledgeGraph()
        threshold = float(os.getenv("KNOWLEDGE_GRAPH_THRESHOLD", "0.8"))
        novel_segments = []

        for seg in keep_segments:
            reasoning = seg.get("reasoning", "")
            if not reasoning:
                novel_segments.append(seg)
                continue
            already_known, _ = kg.check_if_known(reasoning, threshold=threshold)
            if not already_known:
                novel_segments.append(seg)
            else:
                logger.info(f"[Task {task_id}] Skipping known concept: {reasoning[:60]}...")

        if not novel_segments:
            logger.info(f"[Task {task_id}] All segments already in knowledge graph. Nothing new.")
            return True

        logger.info(f"[Task {task_id}] {len(novel_segments)} novel segments after deduplication.")

        # Step 5: AI Co-Host Transition
        logger.info(f"[Task {task_id}] Step 5/7 - Generating AI Co-Host intro...")
        cohost = AICoHost(use_elevenlabs=bool(os.getenv("ELEVENLABS_API_KEY")))
        first_reasoning = novel_segments[0].get("reasoning", "a key insight")
        intro_text = f"Here's something worth your attention. {first_reasoning} Let's get into it."
        tts_audio = await asyncio.to_thread(cohost.generate_transition, intro_text)

        # Step 6: Stitch Audio
        logger.info(f"[Task {task_id}] Step 6/7 - Stitching audio with crossfades...")
        files_to_stitch = []
        if tts_audio and os.path.exists(tts_audio):
            files_to_stitch.append(tts_audio)
        files_to_stitch.append(raw_audio_path)

        final_output = f"data/feed/curated_{task_id}.mp3"
        stitch_ok = await asyncio.to_thread(
            advanced_stitch_with_crossfade, files_to_stitch, final_output
        )
        if not stitch_ok:
            logger.error(f"[Task {task_id}] Audio stitching failed.")
            return False

        # Step 7: Save to Feed DB
        logger.info(f"[Task {task_id}] Step 7/7 - Saving to feed database...")
        title_snippet = novel_segments[0].get("reasoning", "New Insight")[:60]
        tags = _extract_tags(novel_segments)

        add_feed_item(
            item_id=f"seg_{task_id}",
            title=f"Insight: {title_snippet}...",
            source=url,
            audio_url=f"/media/curated_{task_id}.mp3",
            duration=_estimate_duration(novel_segments),
            tags=tags,
            density="Ultra High" if len(novel_segments) >= 3 else "High",
        )

        # Update Knowledge Graph with newly learned concepts
        new_concepts = [seg.get("reasoning", "") for seg in novel_segments if seg.get("reasoning")]
        if new_concepts:
            kg.add_concepts(
                new_concepts,
                metadata=[{"source": url, "task_id": task_id} for _ in new_concepts],
            )
            logger.info(f"[Task {task_id}] Added {len(new_concepts)} concepts to knowledge graph.")

        logger.info(f"[Task {task_id}] Pipeline complete. Feed item: seg_{task_id}")
        return True

    except Exception as exc:
        logger.exception(f"[Task {task_id}] Unhandled pipeline error: {exc}")
        return False


def _extract_tags(segments: list) -> list:
    """Derive simple topic tags from LLM-selected segment reasoning text."""
    common_topics = {
        "ai",
        "llm",
        "machine learning",
        "neuroscience",
        "productivity",
        "startup",
        "investing",
        "health",
        "longevity",
        "focus",
        "habits",
        "crypto",
        "physics",
        "philosophy",
        "psychology",
        "leadership",
    }
    found = set()
    for seg in segments:
        text = seg.get("reasoning", "").lower()
        for topic in common_topics:
            if topic in text:
                found.add(topic.title())
    return list(found)[:5] if found else ["Insight"]


def _estimate_duration(segments: list) -> float:
    """Estimate total curated duration from LLM-provided segment timestamps."""
    total = 0.0
    for seg in segments:
        start = seg.get("start", 0.0)
        end = seg.get("end", 0.0)
        if end > start:
            total += end - start
    return round(total, 1) if total > 0 else 120.0
