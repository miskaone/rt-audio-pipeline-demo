import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Any, Tuple, Callable

# Import codec functionality
from .audio.codecs_auto import get_best_codec, get_codec_by_name

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rt_audio_demo")


# WebSocket security configuration
MAX_FRAME_SIZE = 1_048_576  # 1MB maximum frame size
IDLE_TIMEOUT = 300  # 5 minutes idle timeout

app = FastAPI(title="Real-time Audio Pipeline Demo")


def get_codec_from_query_params(
    query_params: Dict[str, Any]
) -> Tuple[Callable, Callable]:
    """
    Get codec functions based on WebSocket query parameters.

    Args:
        query_params: Dictionary of query parameters from WebSocket connection.

    Returns:
        Tuple of (encode_function, decode_function).
    """
    # Get codec parameter, default to None (use best available)
    codec_param = query_params.get("codec", "").lower()

    if not codec_param:
        # Use best available codec
        return get_best_codec()

    # Map common aliases to standard names
    codec_aliases = {
        "ulaw": "pure_python",
        "mulaw": "pure_python",
        "pure": "pure_python",
        "std": "audioop",
        "stdlib": "audioop",
        "c": "audioop",
        "vectorized": "numpy",
        "np": "numpy"
    }

    # Apply aliases
    codec_name = codec_aliases.get(codec_param, codec_param)

    try:
        # Try to get the requested codec
        return get_codec_by_name(codec_name)
    except ValueError:
        # Fallback to best available if requested codec is not available
        logger.warning(
            "Requested codec '%s' not available, using best available codec",
            codec_param
        )
        return get_best_codec()


@app.get("/health")
async def health():
    return {"status": "ok"}


async def process_chunk(chunk: bytes) -> bytes:
    """Process a single PCM16 audio chunk.

    Args:
        chunk (bytes): Raw PCM16 audio frame received over WebSocket.

    Returns:
        bytes: Processed PCM16 audio frame to send back to the client.
    """
    return chunk


async def example_process_chunk_double(chunk: bytes) -> bytes:
    """Example process_chunk implementation that duplicates the frame.

    This is a tiny example of how you could plug custom logic into the
    audio pipeline. It simply repeats the PCM16 frame back-to-back.

    Args:
        chunk (bytes): Raw PCM16 audio frame received over WebSocket.

    Returns:
        bytes: Duplicated PCM16 audio frame.
    """
    return chunk + chunk


@app.websocket("/ws/audio")
async def audio_websocket(
    ws: WebSocket,
    codec: str = Query(
        None,
        description="Codec to use: audioop, numpy, pure_python",
    ),
):
    """WebSocket endpoint for real-time audio processing.

    Query Parameters:
        codec: Codec implementation to use.
            - audioop: C implementation (fastest, when available)
            - numpy: Vectorized implementation (when available)
            - pure_python: Pure Python implementation (always available)
            - Default: Best available codec

    The endpoint accepts PCM16 audio frames and echoes them back.
    """
    # Parse query parameters
    query_params = {"codec": codec} if codec else {}

    # Get codec functions based on query parameters
    encode_func, decode_func = get_codec_from_query_params(query_params)

    # Determine which codec is being used for logging
    codec_info = {
        "audioop": "audioop (C implementation)",
        "numpy": "NumPy (vectorized)",
        "pure_python": "pure Python",
    }

    # Try to determine the codec name from the function
    codec_name = "unknown"
    codec_candidates = [
        ("audioop", encode_func),
        ("numpy", encode_func),
        ("pure_python", encode_func),
    ]
    for name, func in codec_candidates:
        if getattr(func, "__module__", None) and name in func.__module__:
            codec_name = name
            break

    await ws.accept()
    logger.info(
        "Client connected using %s codec",
        codec_info.get(codec_name, "best available"),
    )

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

            processed = await process_chunk(frame)

            await ws.send_bytes(processed)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception:
        logger.exception("Error in WebSocket handler")
        await ws.close(code=1011)
