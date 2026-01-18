#!/bin/bash

# Automated Resume Screener - Deployment Script
# This script helps you deploy to various free platforms

set -e

echo "🚀 Automated Resume Screener - Deployment Helper"
echo "================================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo "✅ Git repository initialized"
fi

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    echo ""
    echo "1. Go to https://railway.app"
    echo "2. Sign up with GitHub"
    echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
    echo "4. Select this repository"
    echo "5. Set these environment variables:"
    echo "   FLASK_CONFIG=production"
    echo "   SECRET_KEY=$(openssl rand -base64 32)"
    echo "   PORT=5000"
    echo "   HOST=0.0.0.0"
    echo ""
    echo "✅ Railway configuration ready (railway.json created)"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    echo ""
    echo "1. Go to https://render.com"
    echo "2. Sign up with GitHub"
    echo "3. Click 'New' → 'Web Service'"
    echo "4. Connect your GitHub repository"
    echo "5. Render will automatically detect render.yaml"
    echo ""
    echo "✅ Render configuration ready (render.yaml created)"
}

# Function to deploy to Fly.io
deploy_fly() {
    echo "✈️  Deploying to Fly.io..."
    
    # Check if flyctl is installed
    if ! command -v flyctl &> /dev/null; then
        echo "❌ Fly CLI not found. Installing..."
        curl -L https://fly.io/install.sh | sh
        echo "✅ Fly CLI installed. Please restart your terminal and run this script again."
        exit 1
    fi
    
    echo "1. Login to Fly.io:"
    flyctl auth login
    
    echo "2. Launching app..."
    flyctl launch --no-deploy
    
    echo "3. Setting secrets..."
    SECRET_KEY=$(openssl rand -base64 32)
    flyctl secrets set SECRET_KEY="$SECRET_KEY"
    
    echo "4. Deploying..."
    flyctl deploy
    
    echo "5. Opening in browser..."
    flyctl open
    
    echo "✅ Deployed to Fly.io successfully!"
}

# Function to show GitHub setup
setup_github() {
    echo "📁 Setting up GitHub repository..."
    echo ""
    echo "If you haven't already, create a GitHub repository:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository (e.g., 'resume-screener')"
    echo "3. Run these commands:"
    echo ""
    echo "   git remote add origin https://github.com/yourusername/resume-screener.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
}

# Main menu
echo ""
echo "Choose your deployment platform:"
echo "1) Railway (Recommended - Easiest)"
echo "2) Render (Great free tier)"
echo "3) Fly.io (Advanced users)"
echo "4) Setup GitHub first"
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_render
        ;;
    3)
        deploy_fly
        ;;
    4)
        setup_github
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment setup complete!"
echo ""
echo "📚 For detailed instructions, see FREE_DEPLOYMENT_GUIDE.md"
echo "🔧 For troubleshooting, see DEPLOYMENT.md"
echo ""
echo "Happy deploying! 🚀"