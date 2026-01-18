@echo off
echo 🚀 Automated Resume Screener - Deployment Helper
echo ================================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not found. Initializing...
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo ✅ Git repository initialized
)

echo Choose your deployment platform:
echo 1^) Railway ^(Recommended - Easiest^)
echo 2^) Render ^(Great free tier^)
echo 3^) Setup GitHub first
echo 4^) Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto render
if "%choice%"=="3" goto github
if "%choice%"=="4" goto exit
goto invalid

:railway
echo 🚂 Deploying to Railway...
echo.
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click 'New Project' → 'Deploy from GitHub repo'
echo 4. Select this repository
echo 5. Set these environment variables:
echo    FLASK_CONFIG=production
echo    SECRET_KEY=^(generate a secure 32-character key^)
echo    PORT=5000
echo    HOST=0.0.0.0
echo.
echo ✅ Railway configuration ready ^(railway.json created^)
goto end

:render
echo 🎨 Deploying to Render...
echo.
echo 1. Go to https://render.com
echo 2. Sign up with GitHub
echo 3. Click 'New' → 'Web Service'
echo 4. Connect your GitHub repository
echo 5. Render will automatically detect render.yaml
echo.
echo ✅ Render configuration ready ^(render.yaml created^)
goto end

:github
echo 📁 Setting up GitHub repository...
echo.
echo If you haven't already, create a GitHub repository:
echo 1. Go to https://github.com/new
echo 2. Create a new repository ^(e.g., 'resume-screener'^)
echo 3. Run these commands:
echo.
echo    git remote add origin https://github.com/yourusername/resume-screener.git
echo    git branch -M main
echo    git push -u origin main
echo.
goto end

:invalid
echo ❌ Invalid choice. Please run the script again.
goto end

:exit
echo 👋 Goodbye!
goto end

:end
echo.
echo 🎉 Deployment setup complete!
echo.
echo 📚 For detailed instructions, see FREE_DEPLOYMENT_GUIDE.md
echo 🔧 For troubleshooting, see DEPLOYMENT.md
echo.
echo Happy deploying! 🚀
pause