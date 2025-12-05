"""Configuration module for Arabic Voice AI Assistant."""
import os
from pathlib import Path

# Server Configuration
HOST = "0.0.0.0"
PORT = 8080

# Model Paths
TTS_MODEL_PATH = "/root/.local/share/tts/tts_models--ar--custom--egtts_v0.1"
TTS_CONFIG_PATH = "/root/.local/share/tts/tts_models--ar--custom--egtts_v0.1/config.json"
WHISPER_MODEL_SIZE = "medium"
REFERENCE_WAV = "/app/ref.wav"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCVMkDlunj2qvsmP8gf3ExrqoqXmY3aYa0")

# WebRTC Configuration
STUN_SERVERS = [
    "stun:stun.l.google.com:19302",
    "stun:stun1.l.google.com:19302",
    "stun:stun.services.mozilla.com"
]

# Audio Configuration
AUDIO_LANGUAGE = "ar"
TEMP_DIR = "/tmp"

# Gemini Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_SYSTEM_PROMPT = """
تخيل إنك موظف خدمة عملاء مصري ودود بيتكلم باللهجة المصرية الطبيعية، 
بترد باحترام وبلُطف على العميل، ومبتستخدمش فصحى رسمية. 
خلي إجابتك بسيطة، قريبة من كلام الناس العادي، وماتطولش.
حط تشكيل في اللزوم للنطق ومتحطش علامات ترقيم
"""
