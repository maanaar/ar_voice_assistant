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
