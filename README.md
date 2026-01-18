Automating Recruitment: A Data-Driven Resume Screener

## Overview
A comprehensive, AI-powered resume screening system that helps HR professionals efficiently evaluate candidates through automated parsing, intelligent scoring, and advanced analytics. Built with Python/Flask backend and modern web technologies.

## ✨ Key Features

### 🤖 **Intelligent Processing**
- **Multi-format Support**: PDF, DOCX, and TXT resume parsing
- **NLP-powered Analysis**: spaCy-based skill extraction and entity recognition
- **Semantic Matching**: TF-IDF + cosine similarity for job-resume alignment
- **Smart Scoring**: Combines keyword coverage, semantic similarity, and trend analysis

### 📊 **Advanced Analytics**
- **Candidate Clustering**: PCA-based visualization with interactive scatter plots
- **Success Prediction**: Transparent heuristic-based hiring success scores
- **What-If Analysis**: Adjustable scoring weights for different scenarios
- **Fairness Monitoring**: Disparate impact analysis and bias detection

### 🎯 **HR-Focused Features**
- **Gap Detection**: Identifies employment gaps and timeline inconsistencies
- **Flag System**: Highlights missing skills, potential exaggerations, and red flags
- **Batch Processing**: Handle multiple resumes simultaneously
- **Export Capabilities**: CSV downloads for offline analysis

### 🛡️ **Fairness & Compliance**
- **Sensitive Data Redaction**: Automatically removes protected attributes
- **Transparent Scoring**: Explainable AI with detailed breakdowns
- **Bias Mitigation**: Fair comparison through attribute normalization
- **Audit Trail**: Complete scoring explanations for compliance

### 💻 **Modern Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Themes**: Customizable UI preferences
- **Interactive Visualizations**: Canvas-based charts and filtering
- **Real-time Updates**: Live filtering and sorting capabilities

## 🚀 Quick Deployment

### Free Deployment Options

Deploy your resume screener for **FREE** using these platforms:

| Platform | Free Tier | Deployment Time | Difficulty |
|----------|-----------|----------------|------------|
| **Railway** ⭐ | $5/month credit | 5 minutes | Easy |
| **Render** | 750 hours/month | 10 minutes | Easy |
| **Fly.io** | Free allowances | 15 minutes | Medium |

### One-Click Deploy

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy resume screener"
   git remote add origin https://github.com/yourusername/resume-screener.git
   git push -u origin main
   ```

2. **Choose Platform & Deploy**:
   - **Railway**: Connect GitHub repo → Auto-deploy ✨
   - **Render**: Connect GitHub repo → Auto-deploy ✨
   - **Fly.io**: Run `./deploy.sh` (Linux/Mac) or `deploy.bat` (Windows)

3. **Set Environment Variables**:
   ```
   FLASK_CONFIG=production
   SECRET_KEY=your-super-secret-key
   ```

4. **Done!** Your app will be live at `https://your-app.platform.com`

📖 **Detailed Guide**: See [FREE_DEPLOYMENT_GUIDE.md](FREE_DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### 🛠️ Deployment Tools

We've included helpful scripts to make deployment easier:

```bash
# Generate secure environment variables
python setup_env.py

# Test deployment readiness
python test_deployment.py

# Interactive deployment helper
./deploy.sh        # Linux/Mac
deploy.bat         # Windows
```

**Files Created for Easy Deployment**:
- `railway.json` - Railway platform configuration
- `render.yaml` - Render platform configuration  
- `fly.toml` - Fly.io platform configuration
- `.env` - Local environment variables (auto-generated)

---

### Prerequisites
- Python 3.8+ 
- 4GB+ RAM recommended
- Modern web browser

### Automated Setup
```bash
# Clone the repository
git clone <repository-url>
cd automated-resume-screener

# Run automated setup (recommended)
python scripts/setup.py

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Start the application
python run.py
```

### Manual Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR: source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start application
python run.py
# OR: python app.py
```

### Usage
1. **Navigate to HR Dashboard**: Open http://127.0.0.1:5000/dashboard
2. **Input Job Requirements**: 
   - Paste job description
   - Specify must-have skills (comma-separated)
   - List nice-to-have skills (comma-separated)
3. **Upload Resumes**: Select multiple PDF/DOCX/TXT files
4. **Analyze Results**: 
   - Review ranked candidates with scores and explanations
   - Use interactive filters and clustering visualization
   - Export results as CSV for further analysis

## 🏗️ Architecture

### Backend Services
```
services/
├── extract.py      # Multi-format text extraction (PDF/DOCX/TXT)
├── nlp.py         # spaCy-based profile extraction
├── scoring.py     # TF-IDF vectorization and candidate ranking
├── analysis.py    # Gap detection and consistency checks
└── fairness.py    # Bias mitigation and sensitive data redaction
```

### Frontend Components
- **Landing Page**: Feature overview and navigation
- **HR Dashboard**: Main screening interface with analytics
- **Interactive Visualizations**: PCA scatter plots, histograms, fairness charts
- **Responsive Design**: Mobile-first CSS with theme support

### Data Flow
1. **Input Processing**: Job description + resume files → text extraction
2. **NLP Analysis**: Text → structured profiles (skills, education, experience)
3. **Scoring Engine**: Profiles + job requirements → ranked candidates
4. **Analytics Layer**: Clustering, fairness analysis, success prediction
5. **Visualization**: Interactive charts and detailed explanations

## 🔧 Configuration

### Environment Variables
```bash
FLASK_CONFIG=production     # development|production|testing
HOST=0.0.0.0               # Server host
PORT=5000                  # Server port
SECRET_KEY=your-secret-key # Flask secret key
```

### Customization
- **Skills Taxonomy**: Edit `data/skills_master.json`
- **Trending Skills**: Modify `data/skill_trends.json` 
- **Scoring Weights**: Adjust in `config.py` or via What-If interface
- **Fairness Thresholds**: Configure disparate impact rules

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t resume-screener .
docker run -p 5000:5000 resume-screener
```

## 🧪 Testing

```bash
# Run all tests
python scripts/run_tests.py

# Run specific tests
python -m pytest tests/test_basic.py -v

# With coverage
python -m pytest --cov=services --cov=app
```

## 📈 Performance & Scalability

### Current Limits
- **Batch Size**: 50 resumes per upload
- **File Size**: 16MB per resume
- **Text Length**: 50,000 characters per resume
- **Session Storage**: In-memory (suitable for demo/small teams)

### Production Recommendations
- **Database**: Replace in-memory sessions with Redis/PostgreSQL
- **File Storage**: Use cloud storage (AWS S3, Azure Blob)
- **Caching**: Implement vectorizer and model caching
- **Load Balancing**: Deploy behind nginx/Apache for multiple workers
- **Monitoring**: Add logging, metrics, and health checks

## 🛡️ Security & Privacy

### Data Protection
- **Sensitive Redaction**: Automatic removal of protected attributes
- **Local Processing**: No data sent to external APIs
- **Session Isolation**: User data separated by session IDs
- **File Validation**: Type and size checking for uploads

### Compliance Features
- **Audit Logs**: Complete scoring explanations
- **Fairness Metrics**: Disparate impact monitoring
- **Transparent AI**: Explainable scoring algorithms
- **Data Retention**: Configurable session timeouts

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run code formatting
black .

# Run linting
flake8 services/ app.py

# Run tests
pytest tests/ -v
```

### Code Structure
- **Services**: Modular backend components
- **Templates**: Jinja2 HTML templates
- **Static**: CSS, JavaScript, and assets
- **Tests**: Unit and integration tests
- **Scripts**: Setup and utility scripts

## 📋 Roadmap

### Planned Features
- [ ] **Advanced ML Models**: BERT/transformer-based semantic matching
- [ ] **ATS Integration**: Connect with popular applicant tracking systems
- [ ] **Multi-language Support**: Resume parsing in multiple languages
- [ ] **Video Analysis**: CV video screening capabilities
- [ ] **Team Collaboration**: Multi-user workspaces and sharing
- [ ] **Advanced Fairness**: Integration with AIF360/Fairlearn libraries

### Performance Improvements
- [ ] **Async Processing**: Background job processing with Celery
- [ ] **Caching Layer**: Redis for vectorizer and model caching
- [ ] **Database Migration**: PostgreSQL for persistent storage
- [ ] **API Rate Limiting**: Request throttling and quotas

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **spaCy Model Missing**: Run `python -m spacy download en_core_web_sm`
- **PDF Parsing Errors**: Ensure PDFs are text-based, not scanned images
- **Memory Issues**: Reduce batch size or increase system RAM
- **Port Conflicts**: Change PORT environment variable

### Getting Help
- **Documentation**: Check inline code comments and docstrings
- **Issues**: Report bugs and feature requests via GitHub issues
- **Testing**: Use the health check endpoint `/health` for diagnostics

---

**Built with ❤️ for fair and efficient hiring**
