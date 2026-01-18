#!/usr/bin/env python3
"""
Production-ready entry point for the Automated Resume Screener.
Handles environment configuration and graceful startup.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    try:
        import spacy
        # Check if spaCy model is installed
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("✓ spaCy model 'en_core_web_sm' is available")
        except OSError:
            logger.warning("⚠️ spaCy model 'en_core_web_sm' not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            logger.info("✓ spaCy model installed successfully")
    except ImportError:
        logger.error("❌ spaCy not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main entry point."""
    logger.info("🚀 Starting Automated Resume Screener...")
    
    # Check dependencies
    check_dependencies()
    
    # Import and run the Flask app
    try:
        from app import create_app
        app = create_app()
        
        # Configuration
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info("📊 Navigate to /dashboard for the HR interface")
        
        # Start the app
        app.run(host=host, port=port, debug=debug, threaded=True)
        
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()