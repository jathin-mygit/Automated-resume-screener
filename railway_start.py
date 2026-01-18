#!/usr/bin/env python3
"""
Railway-specific startup script
Handles initialization and health checks for Railway deployment
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
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
        logger.info("✓ spaCy imported successfully")
        
        # Check if spaCy model is installed
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("✓ spaCy model 'en_core_web_sm' loaded successfully")
            
            # Test the model with a simple sentence
            doc = nlp("This is a test sentence.")
            logger.info(f"✓ spaCy model test passed: {len(doc)} tokens processed")
            
        except OSError as e:
            logger.error(f"❌ spaCy model 'en_core_web_sm' not found: {e}")
            logger.info("Attempting to download spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            
            # Try loading again
            nlp = spacy.load("en_core_web_sm")
            logger.info("✓ spaCy model downloaded and loaded successfully")
            
    except ImportError as e:
        logger.error(f"❌ spaCy not installed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Dependency check failed: {e}")
        sys.exit(1)

def check_other_imports():
    """Check other critical imports."""
    logger.info("Checking other dependencies...")
    
    try:
        import sklearn
        import numpy
        import pandas
        import flask
        logger.info("✓ All critical dependencies available")
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        sys.exit(1)

def pre_initialize_services():
    """Pre-initialize services to catch errors early."""
    logger.info("Pre-initializing services...")
    
    try:
        # Import and test services
        from services.nlp import load_nlp
        from services.scoring import build_vectorizer
        
        logger.info("Loading NLP model...")
        nlp = load_nlp()
        logger.info("✓ NLP model loaded successfully")
        
        logger.info("Building vectorizer...")
        vectorizer = build_vectorizer()
        logger.info("✓ Vectorizer built successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        return False

def start_application():
    """Start the Flask application."""
    logger.info("Starting Flask application...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Configuration
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Server configuration: {host}:{port}, debug={debug}")
        logger.info("🚀 Starting server...")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    logger.info("🚀 Railway Startup - Automated Resume Screener")
    logger.info("=" * 50)
    
    start_time = time.time()
    
    try:
        # Step 1: Check dependencies
        check_dependencies()
        
        # Step 2: Check other imports
        check_other_imports()
        
        # Step 3: Pre-initialize services (optional, for faster health checks)
        logger.info("Attempting service pre-initialization...")
        if pre_initialize_services():
            logger.info("✓ Services pre-initialized successfully")
        else:
            logger.warning("⚠️ Service pre-initialization failed, will initialize on first request")
        
        # Step 4: Start application
        elapsed = time.time() - start_time
        logger.info(f"Initialization completed in {elapsed:.2f} seconds")
        
        start_application()
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()