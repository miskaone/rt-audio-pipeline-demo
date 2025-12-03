import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rt_audio_demo")


app = FastAPI(title="Real-time Audio Pipeline Demo")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/audio")
async def audio_websocket(ws: WebSocket):
    """
    Very simple WebSocket endpoint that:

    - accepts binary frames (e.g. PCM16 audio)
    - logs the frame size
    - echoes frames back to the client unchanged
    """
    await ws.accept()
    logger.info("Client connected")

    try:
        while True:
            frame = await ws.receive_bytes()
            logger.info("Received %d bytes", len(frame))

            # Echo back exactly what we received
            await ws.send_bytes(frame)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception:
        logger.exception("Error in WebSocket handler")
        await ws.close(code=1011)
