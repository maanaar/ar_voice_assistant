import os, json

models_file = "/root/TTS/.models.json"
os.makedirs("/root/TTS", exist_ok=True)

if os.path.exists(models_file):
    models = json.load(open(models_file))
else:
    models = {"tts_models": {}, "vocoder_models": {}}

models["tts_models"].setdefault("ar", {}).setdefault("custom", {})
models["tts_models"]["ar"]["custom"]["egtts_v0.1"] = {
    "description": "Egyptian Arabic TTS model",
    "default_vocoder": None,
    "license": "mit"
}

with open(models_file, "w") as f:
    json.dump(models, f, indent=4)
