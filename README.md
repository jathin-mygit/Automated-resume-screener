Automating Recruitment: A Data-Driven Resume Screener

Overview
- Minimal, local-first web app that lets HR upload a job description and multiple resumes (PDF/DOCX/TXT), parses them, and returns a ranked list with flags: missing qualifications, employment gaps, duplicate claims, and basic fairness-safe scoring.
- Backend: Python 3 + Flask + spaCy + scikit-learn + pdfminer.six + python-docx
- Frontend: Plain HTML/CSS/JS with responsive, clean UI.

Features
- Upload job description text and multiple resumes
- Extract text from PDF/DOCX/TXT
- NLP-based skill/entity extraction via spaCy
- Keyword + semantic scoring with TF-IDF + cosine similarity
- Prioritized skill matching with hard requirements and nice-to-have skills
- Gap & consistency checks (date ranges, duplicates)
- Bias caution: ignores sensitive terms (gender pronouns, ages if explicitly present) in scoring
- Download CSV of ranked results

Quick start
1) Create and activate a virtual env
   python -m venv .venv
   .venv\\Scripts\\activate

2) Install dependencies
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm

3) Run
   set FLASK_APP=app
   flask run --reload
   # Open http://127.0.0.1:5000

Project structure
- app.py                Flask app
- services/
  - extract.py          PDF/DOCX/TXT text extraction
  - nlp.py              spaCy pipeline and skill extraction
  - scoring.py          vectorizer and scoring logic
  - analysis.py         gaps, duplicates, missing qualifications
- static/
  - styles.css          minimal, eye-pleasing design
- templates/
  - index.html          upload + dashboard
- data/
  - skills_master.json  seed skill taxonomy

Notes
- This is a minimal MVP for demonstration; for production, add user auth, persistent DB, and background job processing.
- For stronger fairness, integrate AIF360 or Fairlearn and redact protected attributes rigorously.
