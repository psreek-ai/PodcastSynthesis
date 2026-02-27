import json
import logging

logging.basicConfig(level=logging.INFO)


def transcribe_audio(audio_path, model_name="base", word_timestamps=True):
    """
    Transcribes the audio file and extracts word-level timestamps.
    Returns the full transcription with segments.
    Whisper is lazily imported here so the server can start without it installed.
    """
    try:
        # Lazy import — whisper only loads when transcription is actually requested
        import whisper

        logging.info(f"Loading Whisper model '{model_name}'...")
        model = whisper.load_model(model_name)

        logging.info(f"Transcribing audio from {audio_path}...")
        result = model.transcribe(audio_path, word_timestamps=word_timestamps)

        return result
    except ImportError:
        logging.warning("Whisper is not installed. Run: pip install openai-whisper")
        logging.warning(
            "Returning empty transcript for now — install Whisper to enable transcription."
        )
        return {"segments": [], "text": ""}
    except Exception as e:
        logging.error(f"Failed to transcribe: {e}")
        return None


def save_transcript_to_file(result, output_path):
    """Saves the structured JSON result containing segments/words."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print("Transcription module loaded.")
