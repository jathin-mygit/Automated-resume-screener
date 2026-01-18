"""
Configuration settings for the Automated Resume Screener.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    # Data directories
    DATA_DIR = BASE_DIR / 'data'
    SKILLS_MASTER_PATH = DATA_DIR / 'skills_master.json'
    SKILL_TRENDS_PATH = DATA_DIR / 'skill_trends.json'
    
    # Processing limits
    MAX_RESUMES_PER_BATCH = 50
    MAX_TEXT_LENGTH = 50000  # characters
    SESSION_TIMEOUT = 3600  # seconds
    
    # NLP settings
    SPACY_MODEL = 'en_core_web_sm'
    TFIDF_MAX_FEATURES = 5000
    
    # Scoring weights (can be overridden by What-If analysis)
    DEFAULT_WEIGHTS = {
        'keyword': 0.5,
        'semantic': 0.35,
        'trend': 0.15
    }
    
    # Fairness thresholds
    DISPARATE_IMPACT_THRESHOLD = 0.8  # 80% rule
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with this config."""
        # Ensure upload directory exists
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True)
        
        # Set Flask config
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['SECRET_KEY'] = cls.SECRET_KEY

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-required'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}