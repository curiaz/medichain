#!/usr/bin/env python3
"""
Test runner script for the MediChain backend
"""
import subprocess
import sys
import os

def run_tests():
    """Run all backend tests"""
    print("🚀 Running MediChain Backend Tests")
    print("=" * 50)

    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)

    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                  check=True, capture_output=True)

    # Run pytest
    print("🧪 Running tests with pytest...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--tb=short'
    ], capture_output=False)

    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(result.returncode)

if __name__ == '__main__':
    run_tests()
