from typing import Iterable, List

BIAS = 0x84  # 132 - standard G.711 bias
CLIP = 32635  # Max value before bias that fits in the encoding range


def _linear_to_mulaw_sample(sample: int) -> int:
    """
    Convert a single 16-bit signed PCM sample to 8-bit μ-law.

    Uses the standard G.711 μ-law encoding algorithm.
    """
    # Extract sign and work with magnitude
    sign = 0x80 if sample < 0 else 0
    if sample < 0:
        sample = -sample

    # Clip to avoid overflow after adding bias
    if sample > CLIP:
        sample = CLIP

    # Add bias for encoding
    sample = sample + BIAS

    # Find the segment (exponent) and quantization level (mantissa)
    # by finding the position of the highest bit
    exponent = 7
    for exp_mask in [0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100]:
        if sample & exp_mask:
            break
        exponent -= 1

    # Extract the 4-bit mantissa from the appropriate position
    mantissa = (sample >> (exponent + 3)) & 0x0F

    # Combine sign, exponent, mantissa and invert (μ-law convention)
    mulaw = ~(sign | (exponent << 4) | mantissa) & 0xFF
    return mulaw


def _mulaw_to_linear_sample(code: int) -> int:
    """
    Convert a single 8-bit μ-law value to 16-bit signed PCM.
    """
    code = ~code & 0xFF

    sign = code & 0x80
    exponent = (code >> 4) & 0x07
    mantissa = code & 0x0F

    # Standard G.711 μ-law decoding formula
    # Reconstruct the magnitude: ((mantissa << 3) | 0x84) << exponent
    # The 0x84 adds the implicit bit (1) and bias adjustment
    sample = ((mantissa << 3) | 0x84) << exponent
    sample -= BIAS

    if sign != 0:
        sample = -sample

    # Clamp to 16-bit range
    if sample > 32767:
        sample = 32767
    if sample < -32768:
        sample = -32768

    return sample


def pcm16_to_mulaw(samples: Iterable[int]) -> bytes:
    """
    Convert an iterable of 16-bit signed PCM samples to μ-law bytes.
    """
    return bytes(_linear_to_mulaw_sample(s) for s in samples)


def mulaw_to_pcm16(data: bytes) -> List[int]:
    """
    Convert μ-law bytes to a list of 16-bit signed PCM samples.
    """
    return [_mulaw_to_linear_sample(b) for b in data]
