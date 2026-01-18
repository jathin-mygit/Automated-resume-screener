#!/usr/bin/env python3
"""
Test runner for the Automated Resume Screener.
"""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests with coverage."""
    print("🧪 Running Automated Resume Screener tests...")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Run tests with coverage
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--cov=services",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ]
        
        result = subprocess.run(cmd, cwd=project_root)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("\n❌ Some tests failed")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)