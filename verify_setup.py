#!/usr/bin/env python3
"""
Verification script to check if the Automated Resume Screener is properly set up.
"""

import sys
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'flask', 'spacy', 'sklearn', 'numpy', 'pandas', 
        'pdfminer', 'docx', 'dateutil'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_spacy_model():
    """Check if spaCy model is available."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model 'en_core_web_sm'")
        return True
    except (ImportError, OSError):
        print("❌ spaCy model 'en_core_web_sm' (missing)")
        return False

def check_project_structure():
    """Check if project files exist."""
    required_files = [
        'app.py', 'config.py', 'run.py',
        'services/__init__.py',
        'services/extract.py',
        'services/nlp.py', 
        'services/scoring.py',
        'services/analysis.py',
        'services/fairness.py',
        'templates/index.html',
        'templates/dashboard.html',
        'static/styles.css',
        'data/skills_master.json',
        'data/skill_trends.json'
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing.append(file_path)
    
    return len(missing) == 0, missing

def main():
    """Main verification function."""
    print("🔍 Verifying Automated Resume Screener Setup")
    print("=" * 50)
    
    all_good = True
    
    # Check Python version
    print("\n📋 Python Version:")
    if not check_python_version():
        all_good = False
    
    # Check dependencies
    print("\n📦 Dependencies:")
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        all_good = False
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_deps)}")
    
    # Check spaCy model
    print("\n🧠 NLP Model:")
    if not check_spacy_model():
        all_good = False
        print("💡 Download model: python -m spacy download en_core_web_sm")
    
    # Check project structure
    print("\n📁 Project Structure:")
    struct_ok, missing_files = check_project_structure()
    if not struct_ok:
        all_good = False
        print(f"💡 Missing files: {', '.join(missing_files)}")
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 Setup verification PASSED!")
        print("🚀 Ready to run: python run.py")
    else:
        print("⚠️  Setup verification FAILED!")
        print("📋 Please address the issues above before running the application")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)