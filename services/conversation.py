"""Audio processing utilities."""
import base64
import tempfile
import os
from typing import Tuple
from models.whisper_model import get_whisper_model


class AudioProcessor:
    """Handles audio processing operations."""
    
    def __init__(self):
        """Initialize audio processor."""
        self.whisper = get_whisper_model()
    
    async def process_audio_input(self, audio_base64: str) -> str:
        """
        Process base64 audio input and transcribe to text.
        
        Args:
            audio_base64: Base64 encoded audio data
            
        Returns:
            Transcribed text
        """
        # Decode base64 to audio data
        audio_data = base64.b64decode(audio_base64)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            # Transcribe audio
            text = self.whisper.transcribe(temp_path)
            return text
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


# Global processor instance
_processor_instance = None


def get_audio_processor() -> AudioProcessor:
    """Get or create global audio processor instance."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = AudioProcessor()
    return _processor_instance