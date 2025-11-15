"""Whisper model wrapper (lazy)."""
import torch
from faster_whisper import WhisperModel
import config

_whisper_instance = None

class WhisperASR:
    def __init__(self):
        # only determine device here, do not load model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

    def _load(self):
        if self.model is None:
            print(f"🎤 Loading Whisper model ({config.WHISPER_MODEL_SIZE}) on {self.device}...")
            self.model = WhisperModel(config.WHISPER_MODEL_SIZE, device=self.device)
            print("✅ Whisper model loaded")

    def transcribe(self, audio_path: str, language: str = "ar") -> str:
        self._load()
        segments, _ = self.model.transcribe(audio_path, language=language)
        return " ".join([seg.text for seg in segments]).strip()

def get_whisper_model() -> WhisperASR:
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = WhisperASR()
    return _whisper_instance
