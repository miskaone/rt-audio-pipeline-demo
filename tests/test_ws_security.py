"""Tests for WebSocket security features and validation."""

import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from app.main import app

client = TestClient(app)


class TestWebSocketSecurity:
    """Test WebSocket security and validation features."""

    def test_reject_oversized_frame(self):
        """WebSocket should reject frames > 1MB with close code 1009."""
        # Create a frame larger than 1MB
        oversized_frame = b"\x00" * (1_048_577)  # 1MB + 1 byte
        
        with client.websocket_connect("/ws/audio") as ws:
            # Send the oversized frame
            ws.send_bytes(oversized_frame)
            
            # Should receive WebSocketDisconnect with code 1009 (Message too big)
            with pytest.raises(WebSocketDisconnect) as exc_info:
                ws.receive_bytes()
            
            assert exc_info.value.code == 1009, f"Expected code 1009, got {exc_info.value.code}"

    def test_accept_max_size_frame(self):
        """WebSocket should accept frames exactly 1MB."""
        # Create a frame exactly 1MB
        max_size_frame = b"\x00" * 1_048_576
        
        with client.websocket_connect("/ws/audio") as ws:
            ws.send_bytes(max_size_frame)
            # Should echo back normally
            echoed = ws.receive_bytes()
            assert echoed == max_size_frame

    def test_accept_normal_size_frame(self):
        """WebSocket should accept normal-sized audio frames."""
        # Normal PCM16 audio frame (20 bytes = 10 samples)
        normal_frame = (
            b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
            b"\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13"
        )

        with client.websocket_connect("/ws/audio") as ws:
            ws.send_bytes(normal_frame)
            echoed = ws.receive_bytes()
            assert echoed == normal_frame

    def test_reject_odd_length_frame(self):
        """WebSocket should reject odd-length frames with close code 1003."""
        # Create a frame with odd byte count (invalid for PCM16)
        odd_frame = b"\x00\x01\x02"  # 3 bytes (odd)

        with client.websocket_connect("/ws/audio") as ws:
            ws.send_bytes(odd_frame)

            # Should receive WebSocketDisconnect with code 1003
            with pytest.raises(WebSocketDisconnect) as exc_info:
                ws.receive_bytes()

            assert (
                exc_info.value.code == 1003
            ), f"Expected code 1003, got {exc_info.value.code}"

    def test_accept_even_length_frames(self):
        """WebSocket should accept even-length frames (valid for PCM16)."""
        # Test various even lengths
        even_frames = [
            b"\x00\x01",           # 2 bytes (1 sample)
            b"\x00\x01\x02\x03",   # 4 bytes (2 samples)
            b"\x00" * 100,         # 100 bytes (50 samples)
        ]

        with client.websocket_connect("/ws/audio") as ws:
            for frame in even_frames:
                ws.send_bytes(frame)
                echoed = ws.receive_bytes()
                assert echoed == frame

    def test_logging_on_validation_errors(self):
        """WebSocket should log appropriate warning messages."""
        import logging
        from io import StringIO

        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("rt_audio_demo")
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        try:
            # Test oversized frame logging
            with client.websocket_connect("/ws/audio") as ws:
                oversized = b"\x00" * (1_048_577)
                ws.send_bytes(oversized)
                with pytest.raises(WebSocketDisconnect):
                    ws.receive_bytes()

            log_output = log_capture.getvalue()
            assert "Frame too large" in log_output
            assert "1048577 bytes" in log_output

            # Clear log capture
            log_capture.seek(0)
            log_capture.truncate(0)

            # Test odd length frame logging
            with client.websocket_connect("/ws/audio") as ws:
                odd_frame = b"\x00\x01\x02"
                ws.send_bytes(odd_frame)
                with pytest.raises(WebSocketDisconnect):
                    ws.receive_bytes()

            log_output = log_capture.getvalue()
            assert "Invalid PCM16 frame" in log_output
            assert "3 bytes" in log_output
            assert "must be even" in log_output

        finally:
            logger.removeHandler(handler)

    def test_timeout_configuration_exists(self):
        """WebSocket should have timeout configuration constants."""
        from app.main import IDLE_TIMEOUT

        # Verify timeout constant exists and is reasonable
        assert hasattr(IDLE_TIMEOUT, '__call__') or isinstance(
            IDLE_TIMEOUT, (int, float)
        )
        if isinstance(IDLE_TIMEOUT, (int, float)):
            assert IDLE_TIMEOUT > 0, "Timeout should be positive"
            assert (
                IDLE_TIMEOUT <= 3600
            ), "Timeout should be reasonable (< 1 hour)"
