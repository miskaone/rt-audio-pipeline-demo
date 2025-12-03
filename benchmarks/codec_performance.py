"""Performance benchmark for codec implementations.

This script benchmarks different codec implementations to measure performance.
"""

import time
import random
import argparse
from typing import List, Dict, Tuple, Callable
import sys

# Add app directory to path for imports
from pathlib import Path

app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

try:
    import audio.codecs_auto as codecs_auto  # type: ignore[import]
except ImportError as e:
    print(f"Error importing codec modules: {e}")
    sys.exit(1)


def generate_test_data(size: int, seed: int = 42) -> List[int]:
    """Generate test PCM16 data."""
    random.seed(seed)
    return [random.randint(-32768, 32767) for _ in range(size)]


def benchmark_codec(
    encode_func: Callable[[List[int]], bytes],
    decode_func: Callable[[bytes], List[int]],
    test_data: List[int],
    name: str,
) -> Dict[str, float]:
    """Benchmark a codec implementation."""
    # Warm up
    encoded = encode_func(test_data[:100])
    decode_func(encoded)

    # Benchmark encoding
    start_time = time.perf_counter()
    for _ in range(10):  # Run multiple times for better measurement
        encoded = encode_func(test_data)
    encode_time = (time.perf_counter() - start_time) / 10

    # Benchmark decoding
    start_time = time.perf_counter()
    for _ in range(10):
        decode_func(encoded)
    decode_time = (time.perf_counter() - start_time) / 10

    # Benchmark round-trip
    start_time = time.perf_counter()
    for _ in range(10):
        encoded = encode_func(test_data)
        decode_func(encoded)
    roundtrip_time = (time.perf_counter() - start_time) / 10

    return {
        'encode_time': encode_time,
        'decode_time': decode_time,
        'roundtrip_time': roundtrip_time,
        'samples_per_second': len(test_data) / roundtrip_time
    }


def print_results(results: List[Tuple[str, Dict[str, float]]], data_size: int):
    """Print benchmark results in a formatted table."""
    print("")
    print(f"Codec Performance Benchmark (data size: {data_size:,} samples)")
    print("=" * 80)
    header = (
        f"{'Codec':<15} {'Encode (s)':<12} "
        f"{'Decode (s)':<12} {'Round-trip (s)':<15} "
        f"{'Samples/s':<12}"
    )
    print(header)
    print("-" * 80)

    for name, result in results:
        row = (
            f"{name:<15} {result['encode_time']:<12.6f} "
            f"{result['decode_time']:<12.6f} "
            f"{result['roundtrip_time']:<15.6f} "
            f"{result['samples_per_second']:<12,.0f}"
        )
        print(row)

    # Find fastest
    fastest = min(results, key=lambda x: x[1]['roundtrip_time'])
    slowest = max(results, key=lambda x: x[1]['roundtrip_time'])
    speedup = slowest[1]['roundtrip_time'] / fastest[1]['roundtrip_time']

    print("-" * 80)
    summary = (
        f"Fastest: {fastest[0]} "
        f"({speedup:.2f}x speedup over {slowest[0]})"
    )
    print(summary)


def main():
    """Run performance benchmarks."""
    parser = argparse.ArgumentParser(
        description="Benchmark codec performance",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10000,
        help="Number of samples to test (default: 10000)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmark with smaller dataset",
    )
    parser.add_argument(
        "--codecs",
        nargs="+",
        choices=["audioop", "numpy", "pure_python", "all"],
        default=["all"],
        help="Codecs to benchmark (default: all)",
    )

    args = parser.parse_args()

    if args.quick:
        args.size = 1000

    # Get codec info
    info = codecs_auto.get_codec_info()
    available_list = ", ".join(info["available_codecs"])
    print(f"Available codecs: {available_list}")
    print(f"Current best: {info['current_best']}")

    # Generate test data
    test_data = generate_test_data(args.size)

    # Determine which codecs to test
    if "all" in args.codecs or args.codecs == ["all"]:
        codecs_to_test = info["available_codecs"]
    else:
        codecs_to_test = [
            codec
            for codec in args.codecs
            if codec in info["available_codecs"]
        ]

    # Benchmark each codec
    results = []

    for codec_name in codecs_to_test:
        try:
            encode_func, decode_func = codecs_auto.get_codec_by_name(codec_name)
            result = benchmark_codec(
                encode_func,
                decode_func,
                test_data,
                codec_name,
            )
            results.append((codec_name, result))
        except Exception as exc:  # pragma: no cover - diagnostic output only
            print(f"Error benchmarking {codec_name}: {exc}")

    if results:
        print_results(results, args.size)
    else:
        print("No benchmarks completed successfully")


if __name__ == '__main__':
    main()
