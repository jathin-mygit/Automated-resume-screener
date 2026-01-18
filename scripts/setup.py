#!/usr/bin/env python3
"""
Setup script for the Automated Resume Screener.
Handles initial setup, dependency installation, and environment configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    if not run_command("python -m venv .venv", "Creating virtual environment"):
        return False
    
    # Provide activation instructions
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        activate_cmd = "source .venv/bin/activate"
    
    print(f"💡 To activate the virtual environment, run: {activate_cmd}")
    return True

def install_dependencies():
    """Install Python dependencies."""
    pip_cmd = ".venv/Scripts/pip" if os.name == 'nt' else ".venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def download_spacy_model():
    """Download spaCy language model."""
    python_cmd = ".venv/Scripts/python" if os.name == 'nt' else ".venv/bin/python"
    
    if not run_command(f"{python_cmd} -m spacy download en_core_web_sm", "Downloading spaCy model"):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = ['uploads', 'logs']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_name}")
        else:
            print(f"✓ Directory already exists: {dir_name}")
    
    return True

def run_tests():
    """Run basic tests to verify setup."""
    python_cmd = ".venv/Scripts/python" if os.name == 'nt' else ".venv/bin/python"
    
    print("🧪 Running basic tests...")
    if run_command(f"{python_cmd} -m pytest tests/test_basic.py -v", "Running tests"):
        print("✓ All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed, but setup is complete")
        return True  # Don't fail setup for test failures

def main():
    """Main setup function."""
    print("🚀 Setting up Automated Resume Screener...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Download spaCy model
    if not download_spacy_model():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    
    if os.name == 'nt':  # Windows
        print("   1. Activate virtual environment: .venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   1. Activate virtual environment: source .venv/bin/activate")
    
    print("   2. Start the application: python run.py")
    print("   3. Open http://127.0.0.1:5000 in your browser")
    print("   4. Navigate to HR Dashboard to start screening resumes")
    print("\n💡 For production deployment, see README.md")

if __name__ == "__main__":
    main()