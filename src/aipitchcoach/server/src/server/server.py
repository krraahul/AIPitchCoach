from fastapi import FastAPI, WebSocket
from voice_agent import process_audio

app = FastAPI()

DURATION = 20 #seconds
SAMPLE_RATE = 16000
intial_buffer = bytearray(DURATION*SAMPLE_RATE)
PROCESSING_CHUNK_SIZE = DURATION * SAMPLE_RATE

audio_view = memoryview(intial_buffer)
bytes_recieved = 0


@app.get("/")
def hello_world():
    return "hello"

@app.websocket('/audio')
async def handle_audio_connection(websocket: WebSocket):
    output = ""
    global bytes_recieved
    global audio_view
    await websocket.accept()
    while True:
        chunks = await websocket.receive_bytes()
        new_bytes_recieved = len(chunks)
        if bytes_recieved < PROCESSING_CHUNK_SIZE:
            audio_view[bytes_recieved: bytes_recieved + new_bytes_recieved] = chunks
            bytes_recieved += new_bytes_recieved
        else:
            audio_to_be_processed = audio_view[:PROCESSING_CHUNK_SIZE]
            audio_view = audio_view[PROCESSING_CHUNK_SIZE:]
            output = process_audio(audio_to_be_processed)
        
        await websocket.send_text("Recieved data" + output)