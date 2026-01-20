import json
from vosk import Model, KaldiRecognizer
from app.config import SAMPLE_RATE
from pathlib import Path

# Load models ONCE (critical) - one per language
# Only load models that exist
MODELS = {}

model_paths = {
    "en": "models/en/vosk-model-small-en-us-0.15",
    "hi": "models/hi/vosk-model-small-hi-0.22",
    "te": "models/te/vosk-model-small-te-0.4",
    "ta": "models/ta/vosk-model-small-ta-0.4",
}

for lang, path in model_paths.items():
    if Path(path).exists():
        try:
            MODELS[lang] = Model(path)
            print(f"✓ Loaded {lang} model")
        except Exception as e:
            print(f"✗ Failed to load {lang} model: {e}")
    else:
        print(f"⊘ {lang} model not found at {path}")

if not MODELS:
    raise RuntimeError("No models loaded! Please download at least one model.")

def create_recognizer(lang: str):
    model = MODELS.get(lang)
    if not model:
        # Fallback to English if language not available
        model = MODELS.get("en")
        if not model:
            available = ", ".join(MODELS.keys())
            raise ValueError(f"Language '{lang}' not available. Available: {available}")
        print(f"⚠ Language '{lang}' not available, using fallback 'en'")
    
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(False)
    return rec

def process_chunk(recognizer, audio_bytes: bytes):
    if recognizer.AcceptWaveform(audio_bytes):
        result = json.loads(recognizer.Result())
        return result.get("text", "")
    else:
        partial = json.loads(recognizer.PartialResult())
        return partial.get("partial", "")
