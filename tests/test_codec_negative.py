"""Tests for codec negative cases and edge conditions."""

import pytest
from app.audio.codecs import pcm16_to_mulaw, mulaw_to_pcm16


class TestMulawCodecNegativeCases:
    """Test codec behavior with invalid inputs and edge cases."""

    def test_encode_invalid_input_type(self):
        """Should raise TypeError for non-iterable input."""
        with pytest.raises(TypeError):
            pcm16_to_mulaw("not a sequence")

    def test_encode_none_input(self):
        """Should raise TypeError for None input."""
        with pytest.raises(TypeError):
            pcm16_to_mulaw(None)

    def test_encode_out_of_range_positive_values(self):
        """Should handle values beyond 16-bit positive range."""
        # Values beyond 32767 should be clipped
        oversized = [50000, 100000, 32768]
        encoded = pcm16_to_mulaw(oversized)
        decoded = mulaw_to_pcm16(encoded)

        # Should be clipped to 16-bit range
        assert all(val <= 32767 for val in decoded)

    def test_encode_out_of_range_negative_values(self):
        """Should handle values beyond 16-bit negative range."""
        # Values beyond -32768 should be clipped
        undersized = [-50000, -100000, -32769]
        encoded = pcm16_to_mulaw(undersized)
        decoded = mulaw_to_pcm16(encoded)

        # Should be clipped to 16-bit range
        assert all(val >= -32768 for val in decoded)

    def test_decode_invalid_input_type(self):
        """Should raise TypeError for non-bytes input."""
        with pytest.raises(TypeError):
            mulaw_to_pcm16("not bytes")

    def test_decode_none_input(self):
        """Should raise TypeError for None input."""
        with pytest.raises(TypeError):
            mulaw_to_pcm16(None)

    def test_decode_empty_input(self):
        """Should handle empty bytes input gracefully."""
        result = mulaw_to_pcm16(b"")
        assert result == []

    def test_encode_contains_non_integers(self):
        """Should handle non-integer values in input sequence."""
        with pytest.raises(TypeError):
            pcm16_to_mulaw([1.5, 2.7, "string"])

    def test_encode_single_out_of_range_value(self):
        """Should clip single out-of-range value correctly."""
        # Test single extreme positive value
        encoded = pcm16_to_mulaw([99999])
        decoded = mulaw_to_pcm16(encoded)
        # Should be close to max after μ-law quantization
        assert decoded[0] >= 32000  # Allow for μ-law quantization error

    def test_encode_single_negative_out_of_range_value(self):
        """Should clip single negative out-of-range value correctly."""
        # Test single extreme negative value
        encoded = pcm16_to_mulaw([-99999])
        decoded = mulaw_to_pcm16(encoded)
        # Should be close to min after μ-law quantization
        assert decoded[0] <= -32000  # Allow for μ-law quantization error


class TestMulawCodecQuantizationError:
    """Test μ-law quantization error bounds for round-trip conversion."""

    def test_round_trip_quantization_error_bounds(self):
        """Round-trip error should be within μ-law quantization limits."""
        import random
        random.seed(42)  # Reproducible

        # Test 100 random samples across the range
        original = [random.randint(-32768, 32767) for _ in range(100)]
        encoded = pcm16_to_mulaw(original)
        decoded = mulaw_to_pcm16(encoded)

        for orig, dec in zip(original, decoded):
            error = abs(dec - orig)
            # μ-law quantization error should be < 5% of absolute value
            # or < 200 for small values (more realistic tolerance)
            tolerance = max(abs(orig) * 0.05, 200)
            assert error < tolerance, (
                f"Quantization error {error} > {tolerance} "
                f"for original value {orig}, decoded {dec}"
            )

    def test_quantization_error_at_extremes(self):
        """Test quantization error at full-scale values."""
        extreme_values = [-32768, -32767, 32766, 32767]

        for val in extreme_values:
            encoded = pcm16_to_mulaw([val])
            decoded = mulaw_to_pcm16(encoded)
            error = abs(decoded[0] - val)

            # At extremes, allow higher tolerance due to μ-law compression
            tolerance = max(abs(val) * 0.05, 500)
            assert error < tolerance, (
                f"Extreme value error {error} > {tolerance} "
                f"for value {val}, decoded {decoded[0]}"
            )

    def test_quantization_error_at_zero(self):
        """Test quantization error near zero (should be minimal)."""
        near_zero_values = [-10, -5, -1, 0, 1, 5, 10]

        for val in near_zero_values:
            encoded = pcm16_to_mulaw([val])
            decoded = mulaw_to_pcm16(encoded)
            error = abs(decoded[0] - val)

            # Near zero, error should be very small
            assert error < 50, (
                f"Near-zero error {error} > 50 "
                f"for value {val}, decoded {decoded[0]}"
            )

    def test_consistent_quantization_error(self):
        """Same input should always produce same output."""
        test_values = [1000, -1000, 16000, -16000]

        for val in test_values:
            # Encode/decode multiple times
            results = []
            for _ in range(5):
                encoded = pcm16_to_mulaw([val])
                decoded = mulaw_to_pcm16(encoded)
                results.append(decoded[0])

            # All results should be identical
            assert all(r == results[0] for r in results), (
                f"Inconsistent quantization for value {val}: {results}"
            )


class TestMulawCodecAPISignature:
    """Test codec API signatures and documentation."""

    def test_pcm16_to_mulaw_signature(self):
        """Verify pcm16_to_mulaw has correct signature."""
        import inspect

        sig = inspect.signature(pcm16_to_mulaw)
        params = list(sig.parameters.keys())

        assert params == ['samples'], f"Expected ['samples'], got {params}"
        assert sig.parameters['samples'].annotation is not None, (
            "Parameter should have type annotation"
        )
        assert sig.return_annotation is not None, (
            "Return type should have type annotation"
        )

    def test_mulaw_to_pcm16_signature(self):
        """Verify mulaw_to_pcm16 has correct signature."""
        import inspect

        sig = inspect.signature(mulaw_to_pcm16)
        params = list(sig.parameters.keys())

        assert params == ['data'], f"Expected ['data'], got {params}"
        assert sig.parameters['data'].annotation is not None, (
            "Parameter should have type annotation"
        )
        assert sig.return_annotation is not None, (
            "Return type should have type annotation"
        )

    def test_pcm16_to_mulaw_docstring(self):
        """Verify pcm16_to_mulaw has proper docstring."""
        doc = pcm16_to_mulaw.__doc__

        assert doc is not None, "pcm16_to_mulaw should have docstring"
        assert "μ-law" in doc or "mulaw" in doc.lower(), (
            "Docstring should mention μ-law"
        )
        assert "PCM" in doc, "Docstring should mention PCM"

    def test_mulaw_to_pcm16_docstring(self):
        """Verify mulaw_to_pcm16 has proper docstring."""
        doc = mulaw_to_pcm16.__doc__

        assert doc is not None, "mulaw_to_pcm16 should have docstring"
        assert "μ-law" in doc or "mulaw" in doc.lower(), (
            "Docstring should mention μ-law"
        )
        assert "PCM" in doc, "Docstring should mention PCM"

    def test_codec_module_imports(self):
        """Verify codec module has proper imports and structure."""
        import app.audio.codecs as codecs_module

        # Check that main functions are exportable
        assert hasattr(codecs_module, 'pcm16_to_mulaw')
        assert hasattr(codecs_module, 'mulaw_to_pcm16')

        # Check that helper functions are private (start with underscore)
        assert hasattr(codecs_module, '_linear_to_mulaw_sample')
        assert hasattr(codecs_module, '_mulaw_to_linear_sample')

        # Check constants exist
        assert hasattr(codecs_module, 'BIAS')
        assert hasattr(codecs_module, 'CLIP')
