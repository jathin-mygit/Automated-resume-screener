#!/usr/bin/env python3
"""
Environment setup script for deployment
Generates secure keys and environment files
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Create .env file for local development"""
    env_content = f"""# Automated Resume Screener - Environment Variables
# Copy these to your deployment platform

# Flask Configuration
FLASK_CONFIG=production
SECRET_KEY={generate_secret_key()}

# Server Configuration
HOST=0.0.0.0
PORT=5000

# File Upload Limits
MAX_CONTENT_LENGTH=16777216
MAX_RESUMES_PER_BATCH=25

# Processing Limits
MAX_TEXT_LENGTH=50000
SESSION_TIMEOUT=3600

# NLP Configuration
SPACY_MODEL=en_core_web_sm
TFIDF_MAX_FEATURES=5000
"""
    
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    return env_content

def create_railway_vars():
    """Generate Railway environment variables"""
    secret_key = generate_secret_key()
    
    vars_content = f"""# Railway Environment Variables
# Copy and paste these in Railway dashboard

FLASK_CONFIG=production
SECRET_KEY={secret_key}
HOST=0.0.0.0
PORT=5000
MAX_CONTENT_LENGTH=16777216
MAX_RESUMES_PER_BATCH=25
"""
    
    print("\n🚂 Railway Environment Variables:")
    print("=" * 40)
    print(vars_content)
    
    return vars_content

def create_render_vars():
    """Generate Render environment variables"""
    secret_key = generate_secret_key()
    
    vars_content = f"""# Render Environment Variables
# Add these in Render dashboard

FLASK_CONFIG=production
SECRET_KEY={secret_key}
HOST=0.0.0.0
PORT=5000
MAX_CONTENT_LENGTH=16777216
MAX_RESUMES_PER_BATCH=25
"""
    
    print("\n🎨 Render Environment Variables:")
    print("=" * 40)
    print(vars_content)
    
    return vars_content

def create_fly_secrets():
    """Generate Fly.io secrets commands"""
    secret_key = generate_secret_key()
    
    commands = f"""# Fly.io Secrets Commands
# Run these commands after 'fly launch'

fly secrets set SECRET_KEY="{secret_key}"
fly secrets set FLASK_CONFIG="production"
fly secrets set MAX_CONTENT_LENGTH="16777216"
fly secrets set MAX_RESUMES_PER_BATCH="25"
"""
    
    print("\n✈️  Fly.io Secrets Commands:")
    print("=" * 40)
    print(commands)
    
    return commands

def save_deployment_vars():
    """Save all deployment variables to a file"""
    deployment_vars = f"""# Automated Resume Screener - Deployment Variables
# Generated on: {os.popen('date').read().strip()}

{create_railway_vars()}

{create_render_vars()}

{create_fly_secrets()}

# Security Notes:
# - Keep these keys secure and private
# - Never commit .env files to git
# - Regenerate keys if compromised
# - Use different keys for different environments
"""
    
    vars_file = Path('deployment_vars.txt')
    with open(vars_file, 'w') as f:
        f.write(deployment_vars)
    
    print(f"\n💾 Saved all variables to {vars_file}")
    return vars_file

def update_gitignore():
    """Update .gitignore to exclude sensitive files"""
    gitignore_content = """
# Environment variables
.env
deployment_vars.txt

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/*
!uploads/.gitkeep

# Logs
*.log
"""
    
    gitignore_file = Path('.gitignore')
    
    # Read existing content if file exists
    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            existing_content = f.read()
    
    # Only add new content if not already present
    if ".env" not in existing_content:
        with open(gitignore_file, 'a') as f:
            f.write(gitignore_content)
        print(f"✅ Updated {gitignore_file}")
    else:
        print(f"✅ {gitignore_file} already configured")

def main():
    """Main setup function"""
    print("🔧 Automated Resume Screener - Environment Setup")
    print("=" * 50)
    
    # Create .env file for local development
    create_env_file()
    
    # Update .gitignore
    update_gitignore()
    
    # Generate deployment variables
    save_deployment_vars()
    
    print("\n🎉 Environment setup complete!")
    print("\n📋 Next Steps:")
    print("1. Review the generated .env file")
    print("2. Choose your deployment platform")
    print("3. Copy the appropriate environment variables")
    print("4. Deploy using the deployment guide")
    
    print("\n⚠️  Security Reminder:")
    print("- Never commit .env or deployment_vars.txt to git")
    print("- Keep your SECRET_KEY secure and private")
    print("- Use different keys for different environments")
    
    print("\n📚 See FREE_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()