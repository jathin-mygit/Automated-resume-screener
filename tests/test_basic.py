"""
Basic tests for the Automated Resume Screener.
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from services.extract import extract_text_from_file
from services.nlp import load_nlp, extract_profile
from services.scoring import build_vectorizer, score_candidates
from services.fairness import redact_sensitive

@pytest.fixture
def app():
    """Create test app."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_page(client):
    """Test index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Automated Resume Screener' in response.data

def test_dashboard_page(client):
    """Test dashboard page loads."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'HR Dashboard' in response.data

def test_text_extraction():
    """Test text extraction from different formats."""
    # Test TXT extraction
    txt_content = b"This is a test resume with Python and SQL skills."
    text = extract_text_from_file("test.txt", txt_content)
    assert "Python" in text
    assert "SQL" in text

def test_nlp_profile_extraction():
    """Test NLP profile extraction."""
    nlp = load_nlp()
    text = "John Doe is a Python developer with 5 years of experience in Django and SQL. He has a Bachelor's degree from MIT."
    
    profile = extract_profile(nlp, text)
    
    assert 'skills' in profile
    assert 'education' in profile
    assert 'experience_ranges' in profile
    
    # Check if skills are detected
    skills = [s.lower() for s in profile['skills']]
    assert 'python' in skills or 'django' in skills or 'sql' in skills

def test_sensitive_redaction():
    """Test sensitive information redaction."""
    text = "John is a 25 years old male developer with email john@example.com"
    result = redact_sensitive(text)
    
    assert '[REDACTED]' in result['redacted']
    assert 'age' in result['notes'] or 'gender' in result['notes']

def test_scoring_basic():
    """Test basic scoring functionality."""
    vectorizer = build_vectorizer()
    
    job_text = "We need a Python developer with Django experience"
    candidates = [
        {
            'filename': 'candidate1.pdf',
            'raw_text_redacted': 'Python Django developer with 3 years experience',
            'skills': ['python', 'django'],
            'experience_ranges': [],
            'flags': []
        }
    ]
    
    results = score_candidates(vectorizer, job_text, candidates, ['python'], ['django'])
    
    assert len(results) == 1
    assert 'overall_score' in results[0]
    assert 'keyword_score' in results[0]
    assert 'semantic_score' in results[0]
    assert results[0]['overall_score'] > 0

def test_api_process_missing_job_description(client):
    """Test API process endpoint with missing job description."""
    response = client.post('/api/process', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_api_analytics_missing_job_description(client):
    """Test API analytics endpoint with missing job description."""
    response = client.post('/api/analytics', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

if __name__ == '__main__':
    pytest.main([__file__])