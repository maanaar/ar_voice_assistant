"""TTS Model wrapper."""
from TTS.api import TTS
import config


class TTSModel:
    """Wrapper for Text-to-Speech model."""
    
    def __init__(self):
        """Initialize TTS model."""
        print("🔊 Loading Arabic TTS model...")
        self.model = TTS(
            model_path=config.TTS_MODEL_PATH,
            config_path=config.TTS_CONFIG_PATH
        )
        print("✅ TTS model loaded.")
    
    def synthesize(self, text: str, output_path: str, speaker_wav: str = None):
        """
        Synthesize text to audio file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            speaker_wav: Reference speaker audio file
        """
        speaker_wav = speaker_wav or config.REFERENCE_WAV
        
        self.model.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=speaker_wav,
            language=config.AUDIO_LANGUAGE
        )


# Global TTS instance
_tts_instance = None


def get_tts_model() -> TTSModel:
    """Get or create global TTS model instance."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSModel()
    return _tts_instance