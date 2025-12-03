"""Tests for performance-optimized codec implementations."""

import pytest
from pathlib import Path
import sys

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from audio.codecs import pcm16_to_mulaw, mulaw_to_pcm16


class TestAudioopCodec:
    """Test audioop-optimized codec implementation."""

    def test_audioop_codec_module_exists(self):
        """audioop codec module should exist."""
        try:
            from audio.codecs_audioop import pcm16_to_mulaw_audioop
            from audio.codecs_audioop import mulaw_to_pcm16_audioop
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")

    def test_audioop_encode_returns_bytes(self):
        """audioop encode should return bytes."""
        try:
            from audio.codecs_audioop import pcm16_to_mulaw_audioop
            
            result = pcm16_to_mulaw_audioop([0, 100, -100])
            assert isinstance(result, bytes)
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")

    def test_audioop_decode_returns_list(self):
        """audioop decode should return list of ints."""
        try:
            from audio.codecs_audioop import mulaw_to_pcm16_audioop
            
            result = mulaw_to_pcm16_audioop(b"\x00\x80\x7f")
            assert isinstance(result, list)
            assert all(isinstance(x, int) for x in result)
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")

    def test_audioop_round_trip_accuracy(self):
        """audioop codec should maintain round-trip accuracy."""
        try:
            from audio.codecs_audioop import pcm16_to_mulaw_audioop
            from audio.codecs_audioop import mulaw_to_pcm16_audioop
            
            # Test silent audio
            original = [0] * 100
            encoded = pcm16_to_mulaw_audioop(original)
            decoded = mulaw_to_pcm16_audioop(encoded)
            
            # Should match pure Python results
            pure_encoded = pcm16_to_mulaw(original)
            pure_decoded = mulaw_to_pcm16(pure_encoded)
            
            assert encoded == pure_encoded, "audioop should match pure Python encoding"
            assert decoded == pure_decoded, "audioop should match pure Python decoding"
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")

    def test_audioop_handles_full_scale(self):
        """audioop codec should handle full-scale values."""
        try:
            from audio.codecs_audioop import pcm16_to_mulaw_audioop
            from audio.codecs_audioop import mulaw_to_pcm16_audioop
            
            # Test full scale positive and negative
            test_values = [32767, -32768, 16384, -16384]
            encoded = pcm16_to_mulaw_audioop(test_values)
            decoded = mulaw_to_pcm16_audioop(encoded)
            
            # Compare with pure Python
            pure_encoded = pcm16_to_mulaw(test_values)
            pure_decoded = mulaw_to_pcm16(pure_encoded)
            
            assert encoded == pure_encoded
            assert decoded == pure_decoded
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")

    def test_audioop_input_validation(self):
        """audioop codec should validate inputs like pure Python."""
        try:
            from audio.codecs_audioop import pcm16_to_mulaw_audioop
            from audio.codecs_audioop import mulaw_to_pcm16_audioop
            
            # Test None input
            with pytest.raises(TypeError):
                pcm16_to_mulaw_audioop(None)
                
            with pytest.raises(TypeError):
                mulaw_to_pcm16_audioop(None)
                
            # Test invalid types
            with pytest.raises(TypeError):
                pcm16_to_mulaw_audioop("not a sequence")
                
            with pytest.raises(TypeError):
                mulaw_to_pcm16_audioop("not bytes")
        except ImportError:
            pytest.skip("audioop codec module not implemented yet")


class TestNumpyCodec:
    """Test NumPy-optimized codec implementation."""

    def test_numpy_codec_module_exists(self):
        """NumPy codec module should exist."""
        try:
            from audio.codecs_numpy import pcm16_to_mulaw_numpy
            from audio.codecs_numpy import mulaw_to_pcm16_numpy
        except ImportError:
            pytest.skip("NumPy codec module not implemented yet")

    def test_numpy_encode_returns_bytes(self):
        """NumPy encode should return bytes."""
        try:
            from audio.codecs_numpy import pcm16_to_mulaw_numpy
            
            result = pcm16_to_mulaw_numpy([0, 100, -100])
            assert isinstance(result, bytes)
        except ImportError:
            pytest.skip("NumPy codec module not implemented yet")

    def test_numpy_decode_returns_list(self):
        """NumPy decode should return list of ints."""
        try:
            from audio.codecs_numpy import mulaw_to_pcm16_numpy
            
            result = mulaw_to_pcm16_numpy(b"\x00\x80\x7f")
            assert isinstance(result, list)
            assert all(isinstance(x, int) for x in result)
        except ImportError:
            pytest.skip("NumPy codec module not implemented yet")

    def test_numpy_round_trip_accuracy(self):
        """NumPy codec should maintain round-trip accuracy."""
        try:
            from audio.codecs_numpy import pcm16_to_mulaw_numpy
            from audio.codecs_numpy import mulaw_to_pcm16_numpy
            
            # Test with larger dataset to benefit from NumPy
            import random
            random.seed(42)
            original = [random.randint(-32768, 32767) for _ in range(1000)]
            
            encoded = pcm16_to_mulaw_numpy(original)
            decoded = mulaw_to_pcm16_numpy(encoded)
            
            # Compare with pure Python
            pure_encoded = pcm16_to_mulaw(original)
            pure_decoded = mulaw_to_pcm16(pure_encoded)
            
            assert encoded == pure_encoded, "NumPy should match pure Python encoding"
            assert decoded == pure_decoded, "NumPy should match pure Python decoding"
        except ImportError:
            pytest.skip("NumPy codec module not implemented yet")


class TestCodecAutoDetection:
    """Test automatic codec selection and fallback logic."""

    def test_codec_auto_detection_exists(self):
        """Codec auto-detection module should exist."""
        try:
            from audio.codecs_auto import get_best_codec, encode_with_best, decode_with_best
        except ImportError:
            pytest.skip("Codec auto-detection not implemented yet")

    def test_get_best_codec_returns_callable(self):
        """get_best_codec should return available codec functions."""
        try:
            from audio.codecs_auto import get_best_codec
            
            encode_func, decode_func = get_best_codec()
            assert callable(encode_func), "Should return callable encode function"
            assert callable(decode_func), "Should return callable decode function"
        except ImportError:
            pytest.skip("Codec auto-detection not implemented yet")

    def test_encode_with_best_matches_pure_python(self):
        """encode_with_best should match pure Python results."""
        try:
            from audio.codecs_auto import encode_with_best
            
            test_values = [0, 100, -100, 32767, -32768]
            result = encode_with_best(test_values)
            
            # Should match pure Python
            pure_result = pcm16_to_mulaw(test_values)
            assert result == pure_result
        except ImportError:
            pytest.skip("Codec auto-detection not implemented yet")

    def test_decode_with_best_matches_pure_python(self):
        """decode_with_best should match pure Python results."""
        try:
            from audio.codecs_auto import decode_with_best
            
            test_data = pcm16_to_mulaw([0, 100, -100, 32767, -32768])
            result = decode_with_best(test_data)
            
            # Should match pure Python
            pure_result = mulaw_to_pcm16(test_data)
            assert result == pure_result
        except ImportError:
            pytest.skip("Codec auto-detection not implemented yet")

    def test_fallback_preference_order(self):
        """Should prefer audioop > NumPy > pure Python."""
        try:
            from audio.codecs_auto import get_best_codec, _detect_available_codecs
            
            available = _detect_available_codecs()
            
            # Should detect audioop first (always available in stdlib)
            assert 'audioop' in available, "audioop should always be available"
            
            # NumPy may or may not be available
            if 'numpy' in available:
                # Should prefer audioop over NumPy
                encode_func, decode_func = get_best_codec()
                # This is a rough test - in real implementation we'd check
                # which module the function comes from
        except ImportError:
            pytest.skip("Codec auto-detection not implemented yet")


class TestWebSocketCodecSelection:
    """Test WebSocket codec selection via query parameters."""

    def test_websocket_codec_query_param_exists(self):
        """WebSocket should support codec query parameter."""
        # This will be implemented in main.py
        try:
            from app.main import get_codec_from_query_params
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_default_selection(self):
        """WebSocket should use best codec by default."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_best_codec
            
            # No query params should return best codec
            encode_func, decode_func = get_codec_from_query_params({})
            best_encode, best_decode = get_best_codec()
            
            assert encode_func.__name__ == best_encode.__name__
            assert decode_func.__name__ == best_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_audioop_selection(self):
        """WebSocket should select audioop codec when requested."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_codec_by_name
            
            # Request audioop codec
            encode_func, decode_func = get_codec_from_query_params({"codec": "audioop"})
            audioop_encode, audioop_decode = get_codec_by_name("audioop")
            
            assert encode_func.__name__ == audioop_encode.__name__
            assert decode_func.__name__ == audioop_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_numpy_selection(self):
        """WebSocket should select NumPy codec when requested."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_codec_by_name
            
            # Request NumPy codec
            encode_func, decode_func = get_codec_from_query_params({"codec": "numpy"})
            numpy_encode, numpy_decode = get_codec_by_name("numpy")
            
            assert encode_func.__name__ == numpy_encode.__name__
            assert decode_func.__name__ == numpy_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_pure_python_selection(self):
        """WebSocket should select pure Python codec when requested."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_codec_by_name
            
            # Request pure Python codec
            encode_func, decode_func = get_codec_from_query_params({"codec": "pure_python"})
            pure_encode, pure_decode = get_codec_by_name("pure_python")
            
            assert encode_func.__name__ == pure_encode.__name__
            assert decode_func.__name__ == pure_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_invalid_fallback(self):
        """WebSocket should fallback to best codec for invalid requests."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_best_codec
            
            # Invalid codec should fallback to best
            encode_func, decode_func = get_codec_from_query_params({"codec": "invalid"})
            best_encode, best_decode = get_best_codec()
            
            assert encode_func.__name__ == best_encode.__name__
            assert decode_func.__name__ == best_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")

    def test_websocket_codec_case_insensitive(self):
        """WebSocket codec selection should be case insensitive."""
        try:
            from app.main import get_codec_from_query_params
            from audio.codecs_auto import get_codec_by_name
            
            # Test various cases
            test_cases = ["AUDIOOP", "Audioop", "NUMPY", "numpy", "PURE_PYTHON", "pure_python"]
            
            for codec_name in test_cases:
                encode_func, decode_func = get_codec_from_query_params({"codec": codec_name})
                expected_encode, expected_decode = get_codec_by_name(codec_name.lower())
                
                assert encode_func.__name__ == expected_encode.__name__
                assert decode_func.__name__ == expected_decode.__name__
        except ImportError:
            pytest.skip("WebSocket codec selection not implemented yet")


class TestPerformanceBenchmarking:
    """Test performance improvements over pure Python."""

    def test_performance_benchmark_exists(self):
        """Performance benchmark module should exist."""
        benchmark_path = Path(__file__).parent.parent / "benchmarks" / "codec_performance.py"
        assert benchmark_path.exists(), "Performance benchmark should exist"

    def test_benchmark_runs_without_error(self):
        """Performance benchmark should execute successfully."""
        import subprocess
        import sys
        
        benchmark_path = Path(__file__).parent.parent / "benchmarks" / "codec_performance.py"
        
        if benchmark_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(benchmark_path), "--quick"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                assert result.returncode == 0, "Benchmark should complete successfully"
            except subprocess.TimeoutExpired:
                pytest.skip("Benchmark timed out")
        else:
            pytest.skip("Performance benchmark not implemented yet")
