import fasttext
from pathlib import Path

MODEL_PATH = "models/langdetect/lid.176.bin"

# Load model only if it exists
if Path(MODEL_PATH).exists():
    model = fasttext.load_model(MODEL_PATH)
    print(f"✓ Language detection model loaded from {MODEL_PATH}")
else:
    print(f"⊘ Language detection model not found at {MODEL_PATH}")
    model = None

def detect_language(text: str):
    """Detect language from text. Returns language code (e.g., 'en', 'hi', 'te', 'ta')"""
    if not model:
        return None
    
    if not text or len(text) < 5:
        return None

    try:
        labels, _ = model.predict(text.replace("\n", " "), k=1)
        lang_code = labels[0].replace("__label__", "")
        return lang_code
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None
