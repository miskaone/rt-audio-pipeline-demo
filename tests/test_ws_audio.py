"""Tests for WebSocket audio endpoint and health check."""

from fastapi.testclient import TestClient

from app.main import app
import app.main as main

client = TestClient(app)


class TestHealthEndpoint:
    """Test /health endpoint."""

    def test_health_returns_ok(self):
        """GET /health should return {"status": "ok"}."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebSocketAudio:
    """Test /ws/audio WebSocket endpoint."""

    def test_ws_audio_echo_simple(self):
        """WebSocket should echo binary frames exactly."""
        with client.websocket_connect("/ws/audio") as ws:
            payload = b"\x01\x02\x03\x04\x05\x06"  # 6 bytes (valid PCM16)
            ws.send_bytes(payload)
            echoed = ws.receive_bytes()
            assert echoed == payload

    def test_ws_audio_echo_pcm16_data(self):
        """WebSocket should echo realistic PCM16 audio data."""
        # Simulate a small PCM16 audio frame (10 samples = 20 bytes)
        import struct
        samples = [0, 1000, -1000, 32767, -32768, 100, -100, 5000, -5000, 0]
        pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)

        with client.websocket_connect("/ws/audio") as ws:
            ws.send_bytes(pcm_bytes)
            echoed = ws.receive_bytes()
            assert echoed == pcm_bytes

    def test_ws_audio_multiple_frames(self):
        """WebSocket should echo multiple frames in order."""
        frames = [
            b"\x00\x01",
            b"\x02\x03\x04\x05",
            b"\x05\x06\x07\x08"
        ]  # All even lengths

        with client.websocket_connect("/ws/audio") as ws:
            for frame in frames:
                ws.send_bytes(frame)
                echoed = ws.receive_bytes()
                assert echoed == frame

    def test_ws_audio_uses_process_chunk(self):
        """WebSocket should pass frames through process_chunk hook."""
        original = main.process_chunk
        main.process_chunk = main.example_process_chunk_double
        try:
            with client.websocket_connect("/ws/audio") as ws:
                payload = b"\x01\x02"  # 2 bytes (valid PCM16 length)
                ws.send_bytes(payload)
                echoed = ws.receive_bytes()
                assert echoed == payload + payload
        finally:
            main.process_chunk = original
