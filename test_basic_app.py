#!/usr/bin/env python3
"""
Basic app functionality test
Tests if the app can start and serve basic endpoints
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_app_creation():
    """Test if the app can be created"""
    print("🧪 Testing app creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        if app:
            print("✅ App created successfully")
            return True
        else:
            print("❌ App creation failed")
            return False
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/health')
            
            if response.status_code == 200:
                print("✅ Health endpoint working")
                data = response.get_json()
                print(f"   Status: {data.get('status')}")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_main_routes():
    """Test main application routes"""
    print("🌐 Testing main routes...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code != 200:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
            # Test dashboard
            response = client.get('/dashboard')
            if response.status_code != 200:
                print(f"❌ Dashboard failed: {response.status_code}")
                return False
            
            print("✅ Main routes working")
            return True
            
    except Exception as e:
        print(f"❌ Routes test error: {e}")
        return False

def test_dependencies():
    """Test critical dependencies"""
    print("📦 Testing dependencies...")
    
    try:
        import flask
        import spacy
        import sklearn
        import numpy
        import pandas
        
        # Test spaCy model
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("test")
        
        print("✅ All dependencies working")
        return True
        
    except Exception as e:
        print(f"❌ Dependencies error: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🧪 Basic App Functionality Test")
    print("=" * 40)
    
    tests = [
        test_dependencies,
        test_app_creation,
        test_health_endpoint,
        test_main_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("✅ Your app should work on Railway")
    else:
        print("⚠️ Some tests failed")
        print("❌ Fix these issues before deploying")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)