"""
Audio download service using yt-dlp.

Supports YouTube, RSS feeds, direct podcast MP3 URLs, and anything yt-dlp handles.
"""

import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def download_audio(url: str, output_path: str) -> bool:
    """
    Download audio from a URL and save it to ``output_path`` as MP3.

    Uses yt-dlp to support YouTube, podcast RSS entries, direct audio links,
    and most other publicly accessible audio sources.

    Args:
        url: The source URL to download from.
        output_path: Full path (including filename) for the output MP3 file.

    Returns:
        True if download succeeded and the file exists, False otherwise.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # yt-dlp template: we want a fixed output path, not a title-based one.
    # Using "-o output_path" directly with "-x --audio-format mp3" achieves this.
    command = [
        "yt-dlp",
        "--no-playlist",  # Don't download entire playlists
        "-x",  # Extract audio only
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",  # Best quality
        "--no-progress",  # Cleaner logs in server context
        "-o",
        output_path,
        url,
    ]

    logger.info(f"Downloading audio from: {url}")
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10-minute max for very long episodes
        )
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Download complete: {output_path} ({size_mb:.1f} MB)")
            return True
        logger.error("yt-dlp exited cleanly but output file not found.")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"Download timed out after 600s for URL: {url}")
        return False
    except subprocess.CalledProcessError as exc:
        logger.error(f"yt-dlp failed (exit {exc.returncode}): {exc.stderr[:500]}")
        return False
    except FileNotFoundError:
        logger.error("yt-dlp not found. Install it: pip install yt-dlp")
        return False


if __name__ == "__main__":
    print("yt-dlp download module loaded.")
