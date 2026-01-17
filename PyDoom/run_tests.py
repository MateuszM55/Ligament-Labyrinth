"""Test runner script for PyDoom project."""

import sys
import subprocess


def run_tests():
    """Run all tests using pytest."""
    print("Running PyDoom tests...")
    print("-" * 50)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=False
    )
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
