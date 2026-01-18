#!/usr/bin/env python3
"""
Production-ready entry point for the Automated Resume Screener.
Handles environment configuration and graceful startup.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import spacy
        # Check if spaCy model is installed
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm' is available")
        except OSError:
            print("⚠️  spaCy model 'en_core_web_sm' not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            print("✓ spaCy model installed successfully")
    except ImportError:
        print("❌ spaCy not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main entry point."""
    print("🚀 Starting Automated Resume Screener...")
    
    # Check dependencies
    check_dependencies()
    
    # Import and run the Flask app
    from app import app
    
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"🌐 Server starting on http://{host}:{port}")
    print("📊 Navigate to /dashboard for the HR interface")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()