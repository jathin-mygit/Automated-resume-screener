#!/usr/bin/env python3
"""
Test script to verify deployment readiness
Run this before deploying to catch common issues
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        'app.py', 'run.py', 'config.py', 'requirements.txt', 
        'Dockerfile', 'templates/dashboard.html', 'templates/index.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_dependencies():
    """Check if all dependencies can be imported"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'flask', 'spacy', 'sklearn', 'numpy', 'pandas', 
        'pdfminer', 'docx', 'rapidfuzz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            elif package == 'docx':
                import docx
            elif package == 'pdfminer':
                import pdfminer
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies available")
        return True

def check_spacy_model():
    """Check if spaCy model is available"""
    print("\n🧠 Checking spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model 'en_core_web_sm' loaded successfully")
        return True
    except OSError:
        print("❌ spaCy model 'en_core_web_sm' not found")
        print("Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"❌ Error loading spaCy model: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check if running in production mode
    flask_config = os.environ.get('FLASK_CONFIG', 'development')
    print(f"  Flask config: {flask_config}")
    
    # Check secret key
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        if len(secret_key) >= 32:
            print("  ✅ SECRET_KEY is properly set")
        else:
            print("  ⚠️  SECRET_KEY is too short (should be 32+ characters)")
    else:
        print("  ⚠️  SECRET_KEY not set (will use default for development)")
    
    # Check port configuration
    port = os.environ.get('PORT', '5000')
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"  Server will run on {host}:{port}")
    
    return True

def test_app_startup():
    """Test if the app can start successfully"""
    print("\n🚀 Testing app startup...")
    
    try:
        # Set test environment
        os.environ['FLASK_CONFIG'] = 'testing'
        
        # Import the app
        from app import create_app
        app = create_app()
        
        # Test app creation
        if app:
            print("✅ App created successfully")
            
            # Test health endpoint
            with app.test_client() as client:
                response = client.get('/health')
                if response.status_code == 200:
                    print("✅ Health endpoint working")
                    return True
                else:
                    print(f"❌ Health endpoint failed: {response.status_code}")
                    return False
        else:
            print("❌ Failed to create app")
            return False
            
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def check_git_status():
    """Check git repository status"""
    print("\n📋 Checking git status...")
    
    if not Path('.git').exists():
        print("❌ Not a git repository. Run: git init")
        return False
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes found:")
            print(result.stdout)
            print("Consider committing changes before deployment")
        else:
            print("✅ No uncommitted changes")
        
        # Check if remote is set
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("✅ Git remote configured")
            print(result.stdout)
        else:
            print("⚠️  No git remote configured")
            print("Add remote: git remote add origin <your-repo-url>")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return False

def generate_deployment_summary():
    """Generate deployment summary and recommendations"""
    print("\n📊 Deployment Summary")
    print("=" * 50)
    
    # Platform recommendations
    print("\n🎯 Recommended Free Platforms:")
    print("1. Railway (https://railway.app)")
    print("   - $5/month free credit")
    print("   - Automatic deployments")
    print("   - Easy setup")
    
    print("\n2. Render (https://render.com)")
    print("   - 750 hours/month free")
    print("   - Automatic SSL")
    print("   - PostgreSQL database")
    
    print("\n3. Fly.io (https://fly.io)")
    print("   - Free allowances")
    print("   - Global deployment")
    print("   - Docker support")
    
    # Environment variables needed
    print("\n🔧 Required Environment Variables:")
    print("FLASK_CONFIG=production")
    print("SECRET_KEY=<32-character-secure-key>")
    print("PORT=5000")
    print("HOST=0.0.0.0")
    
    # Next steps
    print("\n📋 Next Steps:")
    print("1. Push code to GitHub")
    print("2. Choose a deployment platform")
    print("3. Set environment variables")
    print("4. Deploy and test")
    
    print("\n📚 See FREE_DEPLOYMENT_GUIDE.md for detailed instructions")

def main():
    """Main test function"""
    print("🧪 Automated Resume Screener - Deployment Test")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        check_files,
        check_dependencies,
        check_spacy_model,
        check_environment,
        test_app_startup,
        check_git_status
    ]
    
    for check in checks:
        try:
            if not check():
                all_checks_passed = False
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 All checks passed! Ready for deployment!")
    else:
        print("⚠️  Some issues found. Please fix them before deploying.")
    
    generate_deployment_summary()
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)