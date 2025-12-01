FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git wget curl build-essential libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install TTS huggingface_hub uvicorn fastapi soundfile pydub numpy

# Download Egyptian model
RUN python3 - << 'EOF'
from huggingface_hub import snapshot_download
import os, shutil, json

model_path = snapshot_download(repo_id="OmarSamir/EGTTS-V0.1")
target_dir = "/root/.local/share/tts/tts_models--ar--custom--egtts_v0.1"
os.makedirs(target_dir, exist_ok=True)

for f in os.listdir(model_path):
    src = os.path.join(model_path, f)
    dst = os.path.join(target_dir, f)
    if os.path.isfile(src):
        shutil.copy2(src, dst)

cfg_file = os.path.join(target_dir, "config.json")
if not os.path.exists(cfg_file):
    with open(cfg_file, "w") as f:
        json.dump({
            "model": "egtts_v0.1",
            "dataset": "custom",
            "language": "ar",
            "description": "Egyptian Arabic TTS model"
        }, f, indent=4)
EOF

# Register model to Coqui JSON
RUN python3 - << 'EOF'
import json, os
os.makedirs("/root/TTS", exist_ok=True)
models_file = "/root/TTS/.models.json"

if os.path.exists(models_file):
    models = json.load(open(models_file))
else:
    models = {"tts_models": {}, "vocoder_models": {}}

models["tts_models"].setdefault("ar", {}).setdefault("custom", {})
models["tts_models"]["ar"]["custom"]["egtts_v0.1"] = {
    "description": "Egyptian Arabic TTS model",
    "default_vocoder": None,
    "github_rls_url": None,
    "commit": None,
    "license": "mit"
}

with open(models_file, "w") as f:
    json.dump(models, f, indent=4)
EOF

# GPU Env
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose TTS port
EXPOSE 5002

# Run server
CMD ["bash", "-c", "python3 TTS/server/server.py --model_path /root/.local/share/tts/tts_models--ar--custom--egtts_v0.1 --config_path /root/.local/share/tts/tts_models--ar--custom--egtts_v0.1/config.json --port 5002"]
