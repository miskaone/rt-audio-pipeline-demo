"""Audioop-optimized G.711 μ-law codec implementation.

This module provides high-performance μ-law encoding/decoding using
Python's built-in audioop module, which is implemented in C and
offers significant performance improvements over pure Python.

Functions match the pure Python API for drop-in compatibility.

Note: audioop is not available on all Python installations (e.g., Windows).
This module will gracefully fall back to pure Python implementation when
audioop is not available.
"""

from typing import Iterable, List

try:
    import audioop
    AUDIOOP_AVAILABLE = True
except ImportError:
    AUDIOOP_AVAILABLE = False
    # Import pure Python functions as fallback
    from .codecs import _linear_to_mulaw_sample, _mulaw_to_linear_sample


def pcm16_to_mulaw_audioop(samples: Iterable[int]) -> bytes:
    """
    Convert PCM16 samples to μ-law using audioop (C implementation).

    Args:
        samples: Iterable of 16-bit signed PCM samples.

    Returns:
        μ-law encoded bytes.

    Raises:
        TypeError: If input is not iterable or contains non-integer values.
    """
    if not AUDIOOP_AVAILABLE:
        # Fall back to pure Python implementation
        from .codecs import pcm16_to_mulaw
        return pcm16_to_mulaw(samples)

    # Input validation (same as pure Python version)
    if samples is None:
        raise TypeError("Input cannot be None")

    try:
        # Convert to list to check individual elements
        sample_list = list(samples)
    except TypeError:
        raise TypeError("Input must be iterable")

    # Validate each sample and clip to 16-bit range
    validated_samples = []
    for sample in sample_list:
        if not isinstance(sample, int):
            raise TypeError(
                f"All samples must be integers, got {type(sample)}"
            )

        # Clip to 16-bit range
        if sample > 32767:
            sample = 32767
        elif sample < -32768:
            sample = -32768

        validated_samples.append(sample)

    # Convert to bytes (little-endian 16-bit)
    pcm_bytes = b''
    for sample in validated_samples:
        # Convert to unsigned 16-bit for audioop
        if sample < 0:
            sample = sample + 65536
        pcm_bytes += sample.to_bytes(2, byteorder='little', signed=False)

    # Use audioop for μ-law encoding
    mulaw_bytes = audioop.lin2ulaw(pcm_bytes, 2)
    
    return mulaw_bytes


def mulaw_to_pcm16_audioop(data: bytes) -> List[int]:
    """
    Convert μ-law bytes to PCM16 samples using audioop (C implementation).

    Args:
        data: μ-law encoded bytes.

    Returns:
        List of 16-bit signed PCM samples.

    Raises:
        TypeError: If input is not bytes or bytearray.
    """
    if not AUDIOOP_AVAILABLE:
        # Fall back to pure Python implementation
        from .codecs import mulaw_to_pcm16
        return mulaw_to_pcm16(data)

    # Input validation (same as pure Python version)
    if data is None:
        raise TypeError("Input cannot be None")

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Input must be bytes or bytearray")

    # Use audioop for μ-law decoding
    pcm_bytes = audioop.ulaw2lin(data, 2)

    # Convert bytes back to list of integers
    samples = []
    for i in range(0, len(pcm_bytes), 2):
        # Read 16-bit little-endian sample
        sample_bytes = pcm_bytes[i:i+2]
        if len(sample_bytes) == 2:
            sample = int.from_bytes(sample_bytes, byteorder='little', signed=False)
            # Convert back to signed range
            if sample >= 32768:
                sample = sample - 65536
            samples.append(sample)

    return samples
