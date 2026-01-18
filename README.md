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

### Code Structure
- **Services**: Modular backend components
- **Templates**: Jinja2 HTML templates
- **Static**: CSS, JavaScript, and assets
- **Tests**: Unit and integration tests
- **Scripts**: Setup and utility scripts


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

