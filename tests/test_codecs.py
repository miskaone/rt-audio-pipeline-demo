"""Tests for G.711 μ-law codec functions."""

import pytest
from app.audio.codecs import pcm16_to_mulaw, mulaw_to_pcm16


class TestMulawCodecRoundTrip:
    """Test PCM16 → μ-law → PCM16 round-trip accuracy."""

    def test_silent_audio(self):
        """Silent audio (zeros) should round-trip to near-zero values."""
        original = [0, 0, 0]
        encoded = pcm16_to_mulaw(original)
        decoded = mulaw_to_pcm16(encoded)

        assert len(decoded) == len(original)
        # μ-law has a slight bias at zero, allow small deviation
        for val in decoded:
            assert abs(val) < 100, f"Silent sample decoded to {val}, expected near 0"

    def test_full_scale_positive(self):
        """Full-scale positive value should round-trip within 2% tolerance."""
        original = [32767]
        encoded = pcm16_to_mulaw(original)
        decoded = mulaw_to_pcm16(encoded)

        assert len(decoded) == 1
        tolerance = 32767 * 0.02  # 2% of full scale
        assert abs(decoded[0] - original[0]) < tolerance, \
            f"Expected ~{original[0]}, got {decoded[0]}"

    def test_full_scale_negative(self):
        """Full-scale negative value should round-trip within 2% tolerance."""
        original = [-32768]
        encoded = pcm16_to_mulaw(original)
        decoded = mulaw_to_pcm16(encoded)

        assert len(decoded) == 1
        tolerance = 32768 * 0.02  # 2% of full scale
        assert abs(decoded[0] - original[0]) < tolerance, \
            f"Expected ~{original[0]}, got {decoded[0]}"

    def test_mid_range_values(self):
        """Mid-range values should round-trip with reasonable accuracy."""
        original = [8000, -8000, 16000, -16000]
        encoded = pcm16_to_mulaw(original)
        decoded = mulaw_to_pcm16(encoded)

        assert len(decoded) == len(original)
        for orig, dec in zip(original, decoded):
            tolerance = abs(orig) * 0.02  # 2% of the value
            assert abs(dec - orig) < max(tolerance, 100), \
                f"Expected ~{orig}, got {dec}"


class TestMulawCodecBasics:
    """Test basic codec behavior."""

    def test_encode_returns_bytes(self):
        """pcm16_to_mulaw should return bytes."""
        result = pcm16_to_mulaw([1000, 2000, 3000])
        assert isinstance(result, bytes)

    def test_encode_output_length(self):
        """One μ-law byte per PCM16 sample."""
        samples = [100, 200, 300, 400, 500]
        encoded = pcm16_to_mulaw(samples)
        assert len(encoded) == len(samples)

    def test_decode_returns_list_of_ints(self):
        """mulaw_to_pcm16 should return a list of integers."""
        encoded = pcm16_to_mulaw([1000])
        decoded = mulaw_to_pcm16(encoded)
        assert isinstance(decoded, list)
        assert all(isinstance(v, int) for v in decoded)

    def test_empty_input(self):
        """Empty input should produce empty output."""
        assert pcm16_to_mulaw([]) == b""
        assert mulaw_to_pcm16(b"") == []
