import os
import subprocess
from pathlib import Path

def download_audio(url, output_dir="data/audio"):
    """
    Downloads audio from a given URL (YouTube, RSS, or direct Spotify matching via yt-dlp).
    Extracts the best audio format and converts it to mp3.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Best audio, extract audio, audio format mp3
    template = os.path.join(output_dir, "%(title)s.%(ext)s")
    
    command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", template,
        url
    ]
    
    print(f"Downloading audio from {url}...")
    try:
        # Run yt-dlp
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Download successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e.stderr}")
        return False

if __name__ == "__main__":
    # Test with a lightweight, known audio/video source if needed
    print("YT-DLP Downloader initialized.")
