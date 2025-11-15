"""TTS Model wrapper (lazy)."""
from TTS.api import TTS
import config

_tts_instance = None

class TTSModel:
    """Light wrapper for TTS with lazy loading."""

    def __init__(self):
        # don't load heavy model on instantiation
        self._model = None

    def _load(self):
        if self._model is None:
            print("🔊 Loading Arabic TTS model...")
            self._model = TTS(
                model_path=config.TTS_MODEL_PATH,
                config_path=config.TTS_CONFIG_PATH
            )
            print("✅ TTS model loaded.")

    def synthesize(self, text: str, output_path: str, speaker_wav: str = None):
        """Synthesize text to an audio file (lazy loads model)."""
        speaker_wav = speaker_wav or config.REFERENCE_WAV
        self._load()
        # use model's tts_to_file (keeps existing API)
        self._model.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=speaker_wav,
            language=config.AUDIO_LANGUAGE
        )

def get_tts_model() -> TTSModel:
    """Return a global TTSModel singleton (lazy)."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSModel()
    return _tts_instance
