import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rt_audio_demo")


# WebSocket security configuration
MAX_FRAME_SIZE = 1_048_576  # 1MB maximum frame size
IDLE_TIMEOUT = 300  # 5 minutes idle timeout

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

            # Validate frame size
            if len(frame) > MAX_FRAME_SIZE:
                logger.warning(
                    "Frame too large: %d bytes (max: %d)",
                    len(frame), MAX_FRAME_SIZE
                )
                await ws.close(code=1009)  # Message too big
                break

            # Validate PCM16 format (must be even number of bytes)
            if len(frame) % 2 != 0:
                logger.warning(
                    "Invalid PCM16 frame: %d bytes (must be even)",
                    len(frame)
                )
                await ws.close(code=1003)  # Unsupported data
                break
                
            logger.info("Received %d bytes", len(frame))

            # Echo back exactly what we received
            await ws.send_bytes(frame)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception:
        logger.exception("Error in WebSocket handler")
        await ws.close(code=1011)
