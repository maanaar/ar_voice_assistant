"""Whisper ASR Model wrapper."""
import torch
from faster_whisper import WhisperModel
import config


class WhisperASR:
    """Wrapper for Whisper Automatic Speech Recognition."""
    
    def __init__(self):
        """Initialize Whisper model."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎤 Loading Whisper model on {self.device}...")
        self.model = WhisperModel(config.WHISPER_MODEL_SIZE, device=self.device)
        print(f"✅ Whisper model loaded on {self.device}")
    
    def transcribe(self, audio_path: str, language: str = "ar") -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "ar" for Arabic)
            
        Returns:
            Transcribed text
        """
        segments, info = self.model.transcribe(audio_path, language=language)
        text = " ".join([seg.text for seg in segments])
        return text.strip()


# Global Whisper instance
_whisper_instance = None


def get_whisper_model() -> WhisperASR:
    """Get or create global Whisper model instance."""
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = WhisperASR()
    return _whisper_instance