"""Automatic codec selection and fallback logic.

This module provides runtime detection and selection of the best available
codec implementation, following the preference order:
1. audioop (C implementation in stdlib)
2. NumPy (vectorized operations)
3. Pure Python (always available)

Functions provide a unified interface while automatically using the
fastest available implementation.
"""

from typing import Callable, List, Iterable
import logging

# Try to import codec implementations
try:
    from .codecs_audioop import pcm16_to_mulaw_audioop, mulaw_to_pcm16_audioop
    AUDIOOP_AVAILABLE = True
except ImportError:
    AUDIOOP_AVAILABLE = False

try:
    from .codecs_numpy import pcm16_to_mulaw_numpy, mulaw_to_pcm16_numpy
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Pure Python is always available
from .codecs import pcm16_to_mulaw, mulaw_to_pcm16

logger = logging.getLogger(__name__)


def _detect_available_codecs() -> List[str]:
    """Detect which codec implementations are available.

    Returns:
        List of available codec names in order of preference.
    """
    available: List[str] = []

    if AUDIOOP_AVAILABLE:
        available.append("audioop")
        logger.debug("audioop codec available")

    if NUMPY_AVAILABLE:
        available.append("numpy")
        logger.debug("NumPy codec available")

    # Pure Python is always available
    available.append("pure_python")
    logger.debug("pure Python codec available")

    return available


def get_best_codec(query_params: dict = {}) -> tuple[Callable, Callable]:
    """
    Get the best available codec implementation.
    
    Args:
        query_params: Optional dictionary with codec parameter.

    Returns:
        Tuple of (encode_function, decode_function) for the best codec.
    """
    # Get codec parameter, default to None (use best available)
    codec_param = query_params.get("codec", "").lower()

    if not codec_param:
        # Use best available codec
        available = _detect_available_codecs()
        if 'audioop' in available:
            logger.debug("Using audioop codec (C implementation)")
            return pcm16_to_mulaw_audioop, mulaw_to_pcm16_audioop
        elif 'numpy' in available:
            logger.debug("Using NumPy codec (vectorized)")
            return pcm16_to_mulaw_numpy, mulaw_to_pcm16_numpy
        else:
            logger.debug("Using pure Python codec")
            return pcm16_to_mulaw, mulaw_to_pcm16

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
        available = _detect_available_codecs()
        if 'audioop' in available:
            logger.debug("Using audioop codec (C implementation)")
            return pcm16_to_mulaw_audioop, mulaw_to_pcm16_audioop
        elif 'numpy' in available:
            logger.debug("Using NumPy codec (vectorized)")
            return pcm16_to_mulaw_numpy, mulaw_to_pcm16_numpy
        else:
            logger.debug("Using pure Python codec")
            return pcm16_to_mulaw, mulaw_to_pcm16


def get_codec_by_name(name: str) -> tuple[Callable, Callable]:
    """
    Get a specific codec implementation by name.
    
    Args:
        name: Codec name ('audioop', 'numpy', 'pure_python').
        
    Returns:
        Tuple of (encode_function, decode_function).
        
    Raises:
        ValueError: If codec name is not recognized or unavailable.
    """
    name = name.lower()

    if name == 'audioop':
        if not AUDIOOP_AVAILABLE:
            raise ValueError("audioop codec not available")
        return pcm16_to_mulaw_audioop, mulaw_to_pcm16_audioop
    elif name == 'numpy':
        if not NUMPY_AVAILABLE:
            raise ValueError("NumPy codec not available")
        return pcm16_to_mulaw_numpy, mulaw_to_pcm16_numpy
    elif name in ('pure_python', 'pure'):
        return pcm16_to_mulaw, mulaw_to_pcm16
    else:
        raise ValueError(f"Unknown codec: {name}")


def encode_with_best(samples: Iterable[int]) -> bytes:
    """
    Encode PCM16 samples to μ-law using the best available codec.
    
    Args:
        samples: Iterable of 16-bit signed PCM samples.
        
    Returns:
        μ-law encoded bytes.
    """
    encode_func, _ = get_best_codec()
    return encode_func(samples)


def decode_with_best(data: bytes) -> List[int]:
    """
    Decode μ-law bytes to PCM16 using the best available codec.

    Args:
        data: μ-law encoded bytes.

    Returns:
        List of 16-bit signed PCM samples.
    """
    _, decode_func = get_best_codec()
    return decode_func(data)


def encode_with_codec(samples: Iterable[int], codec_name: str) -> bytes:
    """
    Encode PCM16 samples to μ-law using a specific codec.

    Args:
        samples: Iterable of 16-bit signed PCM samples.
        codec_name: Name of codec to use ('audioop', 'numpy', 'pure_python').

    Returns:
        μ-law encoded bytes.
    """
    encode_func, _ = get_codec_by_name(codec_name)
    return encode_func(samples)


def decode_with_codec(data: bytes, codec_name: str) -> List[int]:
    """
    Decode μ-law bytes to PCM16 using a specific codec.

    Args:
        data: μ-law encoded bytes.
        codec_name: Name of codec to use ('audioop', 'numpy', 'pure_python').

    Returns:
        List of 16-bit signed PCM samples.
    """
    _, decode_func = get_codec_by_name(codec_name)
    return decode_func(data)


def get_codec_info() -> dict:
    """
    Get information about available codecs.

    Returns:
        Dictionary with codec availability and selection info.
    """
    available = _detect_available_codecs()
    current_best = available[0] if available else 'pure_python'

    return {
        'available_codecs': available,
        'current_best': current_best,
        'audioop_available': AUDIOOP_AVAILABLE,
        'numpy_available': NUMPY_AVAILABLE,
        'pure_python_available': True
    }
