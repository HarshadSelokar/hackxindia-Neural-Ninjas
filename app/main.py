from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.asr import create_recognizer, process_chunk
from app.lang_detect import detect_language

app = FastAPI()

# Serve static files from frontend directory
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    return FileResponse(frontend_dir / "index.html")

@app.websocket("/stt")
async def stt_ws(websocket: WebSocket):
    await websocket.accept()

    buffer_text = ""
    recognizer = None
    detected_lang = None

    try:
        while True:
            audio = await websocket.receive_bytes()

            # Phase 1: Detect language (only once)
            if not detected_lang:
                temp_rec = create_recognizer("en")
                text = process_chunk(temp_rec, audio)

                if text:
                    buffer_text += " " + text

                # Once we have enough text, detect language
                if len(buffer_text) > 20:
                    detected_lang = detect_language(buffer_text)
                    if detected_lang:
                        recognizer = create_recognizer(detected_lang)
                        await websocket.send_text(f"[LANG:{detected_lang}]")
                    else:
                        # Fallback to English if detection fails
                        detected_lang = "en"
                        recognizer = create_recognizer("en")
                        await websocket.send_text("[LANG:en]")
                continue

            # Phase 2: Normal streaming with detected language
            text = process_chunk(recognizer, audio)
            if text:
                await websocket.send_text(text)

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("Error:", e)
