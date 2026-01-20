from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.asr import create_recognizer, process_chunk

app = FastAPI()

@app.websocket("/stt")
async def stt_ws(websocket: WebSocket):
    await websocket.accept()
    recognizer = create_recognizer()

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            text = process_chunk(recognizer, audio_chunk)

            if text:
                await websocket.send_text(text)

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("Error:", e)
