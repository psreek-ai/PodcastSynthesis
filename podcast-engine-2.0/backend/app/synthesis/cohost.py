import os
import requests
import uuid
import logging

logging.basicConfig(level=logging.INFO)

class AICoHost:
    def __init__(self, use_elevenlabs=True):
        """
        Initializes the AI Co-Host module.
        Defaults to ElevenLabs for viral-quality hyper-realistic voices.
        Falls back to local/other TTS later if needed.
        """
        self.use_elevenlabs = use_elevenlabs
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        # Default clear narrator voice ID
        self.voice_id = "TNQX694VP61R6o4D2n38" 

    def generate_transition(self, context_text, output_dir="data/tts"):
        """
        Generates an audio bridge.
        E.g., "That was deep. Now let's switch gears and hear from Naval on wealth creation."
        """
        os.makedirs(output_dir, exist_ok=True)
        filename = f"cohost_transition_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(output_dir, filename)

        if not self.use_elevenlabs or not self.api_key:
            logging.warning("ElevenLabs API Key missing or disabled. Skipping AI Co-Host.")
            # For local GitHub testing fallback, you could use Pyttsx3 or whisper TTS
            return None

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": context_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            logging.info(f"Generating AI Co-Host transition audio...")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logging.info(f"Co-Host audio saved to {filepath}")
                return filepath
            else:
                 logging.error(f"TTS Failed: {response.text}")
                 return None
                 
        except Exception as e:
            logging.error(f"Error during TTS generation: {e}")
            return None

if __name__ == "__main__":
    print("AI Co-Host TTS module loaded.")
