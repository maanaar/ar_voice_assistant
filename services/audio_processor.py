"""Audio processing utilities (lazy whisper)."""
import base64
import tempfile
import os
from models.whisper_model import get_whisper_model

class AudioProcessor:
    """Handles audio processing operations."""

    def __init__(self):
        # don't load whisper here
        pass

    async def process_audio_input(self, audio_base64: str) -> str:
        """Decode base64 audio, save temp file, transcribe with whisper."""
        audio_data = base64.b64decode(audio_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            whisper = get_whisper_model()  # lazy load on first call
            text = whisper.transcribe(temp_path)
            return text
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

_processor_instance = None

def get_audio_processor() -> AudioProcessor:
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = AudioProcessor()
    return _processor_instance
