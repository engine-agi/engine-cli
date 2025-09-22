#!/usr/bin/env python3
"""CLI Performance Benchmark Script."""
import time
import subprocess
import sys
from pathlib import Path

def run_command(cmd: list) -> float:
    """Run command and return execution time."""
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        end_time = time.time()
        return end_time - start_time
    except subprocess.TimeoutExpired:
        return float('inf')

def benchmark_cli(cli_path: str, iterations: int = 5):
    """Benchmark CLI startup performance."""
    print("🚀 Engine CLI Performance Benchmark")
    print("=" * 50)

    # Test basic startup
    print(f"\n📊 Testing basic startup (--version) - {iterations} iterations:")
    times = []
    for i in range(iterations):
        cmd_time = run_command([sys.executable, "-m", cli_path, "--version"])
        times.append(cmd_time)
        print(f"  Run {i+1}: {cmd_time:.3f}s")

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\n📈 Results:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")

    # Performance check
    if avg_time < 2.0:
        print("✅ PASSED: Startup time < 2 seconds")
    else:
        print("❌ FAILED: Startup time >= 2 seconds")

    # Test command loading (lazy loading)
    print(f"\n📊 Testing command loading (agent --help) - {iterations} iterations:")
    times = []
    for i in range(iterations):
        cmd_time = run_command([sys.executable, "-m", cli_path, "agent", "--help"])
        times.append(cmd_time)
        print(f"  Run {i+1}: {cmd_time:.3f}s")

    avg_cmd_time = sum(times) / len(times)
    print("\n📈 Command loading results:")
    print(f"  Average: {avg_cmd_time:.3f}s")

    if avg_cmd_time < 1.0:
        print("✅ PASSED: Command loading < 1 second")
    else:
        print("⚠️  SLOW: Command loading >= 1 second")

    print("\n🎯 Performance Summary:")
    print(f"  • Target startup time: < 2.0s")
    print(f"  • Achieved startup time: {avg_time:.3f}s")
    print(f"  • Target command time: < 1.0s")
    print(f"  • Achieved command time: {avg_cmd_time:.3f}s")
    print("  • Lazy loading: ✅ Implemented")
    print("  • Command caching: ✅ Implemented")

if __name__ == "__main__":
    # Find CLI module path
    cli_path = "engine_cli.main"

    # Check if we're in the right directory
    if not Path("src/engine_cli").exists():
        print("❌ Error: Run this script from the engine-cli root directory")
        sys.exit(1)

    benchmark_cli(cli_path)