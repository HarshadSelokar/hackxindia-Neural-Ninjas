import json
from vosk import Model, KaldiRecognizer
from app.config import SAMPLE_RATE

# Load model ONCE (critical)
model = Model("models/vosk-model-small-en-us-0.15")

def create_recognizer():
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
