import logging
import os
import struct
import uuid

import requests

logging.basicConfig(level=logging.INFO)


class AICoHost:
    def __init__(self, use_elevenlabs=True):
        """
        Initializes the AI Co-Host module.

        Priority order for TTS:
          1. ElevenLabs (highest quality, requires ELEVENLABS_API_KEY)
          2. Google Gemini Flash TTS (free fallback, requires GEMINI_API_KEY)
             Inspired by PodcastKnowledgeDistiller's Gemini TTS integration.
          3. Silent / no audio (last resort)
        """
        self.use_elevenlabs = use_elevenlabs
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        # Default clear narrator voice ID
        self.voice_id = "TNQX694VP61R6o4D2n38"

    def generate_transition(self, context_text, output_dir="data/tts"):
        """
        Generates an audio bridge.
        E.g., "That was deep. Now let's switch gears and hear from Naval on wealth creation."

        Falls back from ElevenLabs → Gemini Flash TTS → None in that order.
        """
        os.makedirs(output_dir, exist_ok=True)

        if self.use_elevenlabs and self.api_key:
            return self._generate_elevenlabs(context_text, output_dir)

        if self.gemini_api_key:
            logging.info("ElevenLabs not configured. Falling back to Gemini Flash TTS.")
            return self._generate_gemini(context_text, output_dir)

        logging.warning("No TTS API keys configured (ELEVENLABS_API_KEY or GEMINI_API_KEY). Skipping Co-Host audio.")
        return None

    def _generate_elevenlabs(self, context_text, output_dir):
        filename = f"cohost_transition_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(output_dir, filename)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        data = {
            "text": context_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        try:
            logging.info("Generating AI Co-Host transition audio via ElevenLabs...")
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logging.info(f"Co-Host audio saved to {filepath}")
                return filepath
            else:
                logging.error(f"ElevenLabs TTS failed: {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error during ElevenLabs TTS: {e}")
            return None

    def _generate_gemini(self, context_text, output_dir):
        """
        Generates TTS audio using Google Gemini 2.5 Flash (free tier available).
        Returns a WAV file path, or None on failure.
        Voice: 'Zephyr' — clear, neutral narrator.
        """
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            logging.warning("google-genai not installed. Run: pip install google-genai")
            return None

        filename = f"cohost_transition_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(output_dir, filename)

        try:
            logging.info("Generating AI Co-Host transition audio via Gemini Flash TTS...")
            client = genai.Client(api_key=self.gemini_api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=context_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Zephyr"
                            )
                        )
                    ),
                ),
            )

            # Extract raw PCM audio data from the response
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            wav_bytes = _pcm_to_wav(audio_data, sample_rate=24000, channels=1, bit_depth=16)

            with open(filepath, "wb") as f:
                f.write(wav_bytes)

            logging.info(f"Gemini TTS Co-Host audio saved to {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"Error during Gemini TTS generation: {e}")
            return None


def _pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bit_depth: int = 16) -> bytes:
    """
    Wraps raw PCM bytes in a WAV file header.
    Mirrors the pcmToWav() helper from PodcastKnowledgeDistiller's geminiService.ts.
    """
    byte_rate = sample_rate * channels * (bit_depth // 8)
    block_align = channels * (bit_depth // 8)
    data_size = len(pcm_data)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,           # Subchunk1Size (PCM)
        1,            # AudioFormat (PCM = 1)
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bit_depth,
        b"data",
        data_size,
    )
    return header + pcm_data


if __name__ == "__main__":
    print("AI Co-Host TTS module loaded.")
