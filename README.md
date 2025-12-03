# Real-time Audio Pipeline Demo

Small demo project that shows a few core building blocks for voice work:

- PCM16 and G.711 μ-law conversion helpers
- A WebSocket endpoint that accepts and echoes raw audio frames
- HTTP health check endpoint
- A couple of tests to prove the audio helpers behave as expected

This is not a full media server. It is meant to be a simple, readable example.

## Why This Exists

This demo illustrates the fundamental building blocks needed for real-time voice applications:

- **WebSocket audio streaming** - Low-latency bidirectional audio transport
- **G.711 μ-law codec** - Telephony-standard compression (8:1 ratio, widely supported)
- **PCM16 handling** - The baseline format most audio systems use

Use this as a learning reference or starting point for:
- Voice bot backends
- Call recording services
- Audio transcription pipelines
- WebRTC gateway prototypes

## Features

- FastAPI app with HTTP and WebSocket endpoints
- Binary WebSocket frames treated as 16-bit PCM audio chunks
- G.711 μ-law encode/decode helpers in pure Python
- Tests for round-trip μ-law conversion and a basic WebSocket echo
- Automatic codec selection (audioop / NumPy / pure Python) with
  performance benchmarks

## Project Structure

```
app/
├── main.py              # FastAPI app and WebSocket endpoint
├── audio/
│   ├── codecs.py        # Core PCM16 ↔ μ-law conversion helpers
│   ├── codecs_audioop.py  # audioop-accelerated μ-law helpers
│   ├── codecs_numpy.py    # NumPy-aware μ-law helpers
│   └── codecs_auto.py     # automatic codec selection logic
tests/
├── test_codecs.py         # Audio codec tests
├── test_codec_negative.py # Negative and quantization tests
├── test_codec_performance.py # Codec performance and selection tests
└── test_ws_audio.py       # WebSocket and health endpoint tests
benchmarks/
└── codec_performance.py # Simple codec performance benchmark script
requirements.txt
Dockerfile
README.md
```

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or use the Makefile:

```bash
make install
```

## Usage

Run the development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Or use the Makefile:

```bash
make run
```

### Health Check

- **URL**: `GET /health`
- **Response**: `{"status": "ok"}`
- **Purpose**: Verify the service is running (useful for load balancers, monitoring)

Example:
```bash
curl http://localhost:8001/health
```

### WebSocket Audio

- **URL**: `WS /ws/audio`
- **Direction**: Bidirectional
- **Frame type**: Binary
- **Payload**: Raw 16-bit signed little-endian PCM samples

The server does not interpret the audio content. It logs frame sizes and echoes the bytes back immediately.

**Audio format details:**
- Sample format: 16-bit signed PCM (little-endian)
- Sample rate: Any rate works (commonly 8kHz, 16kHz, or 48kHz)
- Channels: Mono recommended (server treats all bytes as raw samples)
- Frame size: Any size (typically 160-480 bytes for 10-30ms chunks)

Example connection (using `websocat`):
```bash
websocat ws://localhost:8001/ws/audio
```
#### Codec selection and performance tiers

By default, the server chooses the **best available codec implementation** in
this order:

1. `audioop` – C implementation from the Python stdlib (fastest)
2. `numpy` – vectorized implementation when NumPy is installed
3. Pure Python – always available, maximally portable

You can explicitly select a codec using the `codec` query parameter on the
WebSocket URL:

- `ws://localhost:8001/ws/audio?codec=audioop`
- `ws://localhost:8001/ws/audio?codec=numpy`
- `ws://localhost:8001/ws/audio?codec=pure_python`

If the requested codec is not available on the current environment, the
server falls back to the best available option.

#### Benchmarking codec performance

To compare the different implementations, use the benchmark script:

```bash
python benchmarks/codec_performance.py --quick
```

This prints a small table showing encode/decode and round-trip timings plus
estimated samples per second for each available codec.

## Development

### Running Tests

Run all tests with:

```bash
pytest
```

Or use the Makefile:

```bash
make test
```

### Code Quality

Format code and run linting:

```bash
make check
```

Or run separately:
```bash
make format  # Format code with black
make lint    # Run linting checks
```

### Clean Up

Remove temporary files:

```bash
make clean
```

Tests cover:

- μ-law encode/decode round trips for silent audio (0), full-scale (±32767), and mid-range values
- WebSocket security and validation tests
- Input validation and error handling
- Quantization error bounds
- API signature validation

## Docker

Build and run using Docker:

```bash
docker build -t rt-audio-pipeline-demo .
docker run -p 8001:8001 rt-audio-pipeline-demo
```

Then connect to:
- Health: `http://localhost:8001/health`
- WebSocket: `ws://localhost:8001/ws/audio`

## G.711 μ-law Background

G.711 μ-law (mu-law) is a logarithmic audio codec standardized for telephony:
- **Compression**: 8:1 (16-bit PCM → 8-bit μ-law)
- **Sample rate**: Typically 8kHz in telephony
- **Quality**: Good for voice, not suitable for music
- **Use cases**: VoIP, PSTN gateways, legacy phone systems

The codec implementations in this project are pure Python for educational clarity, not optimized for production use.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
