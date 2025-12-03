# Real-time Audio Pipeline Demo - Agent Spec

## Goal

Build a small FastAPI service that demonstrates core audio pipeline building blocks:
- A `/ws/audio` WebSocket endpoint that echoes binary frames
- Simple PCM16 ↔ G.711 μ-law conversion helpers
- A couple of tests for codecs and WebSocket echo

Keep it small, readable, and focused on educational clarity over production optimization.

## Scope

**In scope:**
- Backend only (FastAPI service)
- WebSocket audio streaming
- G.711 μ-law codec implementation
- Basic tests

**Out of scope:**
- Frontend/UI
- Database
- Authentication/authorization
- Production-grade error handling
- Audio processing (VAD, noise reduction, etc.)
- Multiple codec support beyond μ-law

## Stack

- **Python**: 3.12+
- **Web framework**: FastAPI
- **ASGI server**: Uvicorn
- **Testing**: pytest
- **Container**: Docker (Alpine-based for small image size)

## Requirements

### HTTP Endpoints

#### Health Check
- **Route**: `GET /health`
- **Response**: `{"status": "ok"}` (JSON)
- **Purpose**: Service health verification for monitoring/load balancers

### WebSocket Endpoints

#### Audio Streaming
- **Route**: `/ws/audio`
- **Protocol**: Binary WebSocket frames
- **Behavior**: 
  - Accept binary frames containing raw PCM16 audio samples
  - Log each frame's byte size to stdout
  - Echo the exact bytes back to the client immediately (no buffering)
  - Each incoming frame is echoed as a separate outgoing frame

**Audio format expectations:**
- Sample format: 16-bit signed integers (little-endian)
- Sample rate: Agnostic (8kHz, 16kHz, or 48kHz all work)
- Channels: Mono (server doesn't interpret channels, just treats as byte stream)
- Frame size: Variable (typically 160-960 bytes for 10-60ms audio chunks)

### Audio Codec Module

**Module**: `app/audio/codecs.py`

**Functions:**

```python
def pcm16_to_mulaw(samples: Iterable[int]) -> bytes:
    """
    Convert 16-bit signed PCM samples to G.711 μ-law bytes.
    
    Args:
        samples: Iterable of 16-bit signed integers (-32768 to 32767)
    
    Returns:
        bytes: μ-law encoded audio (one byte per sample)
    """
    pass

def mulaw_to_pcm16(data: bytes) -> list[int]:
    """
    Convert G.711 μ-law bytes back to 16-bit signed PCM samples.
    
    Args:
        data: μ-law encoded audio bytes
    
    Returns:
        list[int]: 16-bit signed PCM samples
    """
    pass
```

**Implementation notes:**
- Pure Python implementation (no native extensions)
- Use standard G.711 μ-law lookup tables or formula
- Prioritize code clarity over performance

### Tests

**Location**: `tests/` directory

**Required test coverage:**

1. **Codec round-trip tests** (`test_codecs.py`):
   - Silent audio: `[0, 0, 0]` → μ-law → PCM16 (should be close to original)
   - Full-scale positive: `[32767]` → μ-law → PCM16
   - Full-scale negative: `[-32768]` → μ-law → PCM16
   - Mid-range values: `[8000, -8000, 16000, -16000]` → μ-law → PCM16
   - Assert decoded values are within acceptable tolerance (±2% for full scale)

2. **WebSocket echo test** (`test_websocket.py`):
   - Use FastAPI's `TestClient` with WebSocket support
   - Connect to `/ws/audio`
   - Send binary frame with sample PCM16 data
   - Assert echoed frame matches sent data exactly

### Dependencies

**Core** (`requirements.txt`):
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server with WebSocket support
- `pytest` - Testing framework
- `httpx` - Required for TestClient WebSocket support

**Keep dependencies minimal** - no ML libraries, no heavy audio processing frameworks.

### Container

**Dockerfile requirements:**
- Base: `python:3.12-alpine` (for small image size)
- Copy only necessary files (use `.dockerignore`)
- Expose port 8001
- CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
- Build time: Should complete in <2 minutes on typical hardware

### Documentation

**README.md should include:**
- Project overview and purpose
- "Why this exists" / use cases section
- Quick start instructions (venv setup, install, run)
- Endpoint documentation (health check + WebSocket)
- Audio format specifications
- Test execution instructions
- Docker build and run commands
- Brief G.711 μ-law background context

## Constraints

- **Code size**: Keep total codebase under 400-600 lines (excluding tests and config)
- **Simplicity**: Flat module structure, no framework abstractions beyond FastAPI basics
- **Dependencies**: Only include what's absolutely necessary
- **Performance**: Not a concern for this demo (clarity > speed)
- **Error handling**: Basic error logging is sufficient (no retry logic, circuit breakers, etc.)

## File Structure

Expected layout:

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, health endpoint, WebSocket handler
│   └── audio/
│       ├── __init__.py
│       └── codecs.py        # PCM16 ↔ μ-law conversion functions
├── tests/
│   ├── __init__.py
│   ├── test_codecs.py       # Codec round-trip tests
│   └── test_websocket.py    # WebSocket echo test
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## Development approach (TDD)

## Follow a simple TDD loop:

1. Write tests first for:
   - μ-law codec behavior
   - WebSocket echo behavior
2. Run tests and confirm they fail.
3. Implement the minimum code needed to make the tests pass.
4. Refactor if needed, keeping tests green.

Do not add features that are not covered by tests.

## Success Criteria

✅ Service starts and responds to `/health` with 200 OK  

✅ WebSocket accepts connection at `/ws/audio`  

✅ Binary frames are logged and echoed back correctly 

✅ μ-law codec converts PCM16 → μ-law → PCM16 with acceptable accuracy  

✅ All tests pass with `pytest`  

✅ Docker image builds and runs successfully  

✅ README provides clear setup and usage instructions  

✅ Code is readable and well-commented where logic is non-obvious  

## Non-Goals

- Production deployment configuration (K8s, scaling, etc.)
- Audio quality analysis or metrics
- Multi-codec support (only μ-law required)
- Streaming protocol negotiation (fixed format)
- Client-side code or examples
- Performance benchmarking
