from typing import Dict, List
import re
import json
from pathlib import Path
import spacy

SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_master.json"


def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # model not installed; fall back to blank pipeline with sentencizer
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp


def _load_skill_taxonomy() -> List[str]:
    if SKILLS_PATH.exists():
        try:
            data = json.loads(SKILLS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [s.lower() for s in data]
        except Exception:
            pass
    # fallback minimal skills
    return [
        "python", "java", "javascript", "react", "node", "django", "flask",
        "sql", "mysql", "postgresql", "mongodb", "nlp", "spacy", "pytorch",
        "tensorflow", "scikit-learn", "git", "docker", "kubernetes", "aws",
        "azure", "gcp", "html", "css", "linux", "rest", "fastapi", "opencv"
    ]


SKILL_TAXONOMY = set(_load_skill_taxonomy())


def extract_profile(nlp, text: str) -> Dict:
    # Simple extraction: skills via fuzzy/regex, education/experience via section heuristics, dates
    lowered = text.lower()

    # Skills extraction
    skills_found = set()
    for token in re.split(r"[^a-zA-Z0-9+#\.\-]", lowered):
        if not token:
            continue
        if token in SKILL_TAXONOMY:
            skills_found.add(token)
    # Multi-word skills pass
    multi = [
        "machine learning", "data science", "deep learning", "natural language processing",
        "computer vision", "project management", "data analysis", "web development",
    ]
    for phrase in multi:
        if phrase in lowered:
            skills_found.add(phrase)

    # Education section detection (heuristic)
    education = []
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if re.search(r"(b\.?tech|b\.?e\.?|m\.?tech|bachelor|master|ph\.?d|degree|university|college)", l, re.I):
            education.append(l)

    # Experience extraction via date ranges, scoped to Experience section, avoiding Projects
    date_pat = re.compile(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}", re.I)
    range_pat = re.compile(r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})\s*[\u2013\-to]+\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|present|current)", re.I)
    exp_head = re.compile(r"\b(experience|work experience|employment|employment history|professional experience|work history|internship|internships)\b", re.I)
    proj_head = re.compile(r"\b(projects?|academic projects?|capstone|thesis|coursework|academic)\b", re.I)
    employment_kw = re.compile(r"\b(employer|company|role|position|engineer|developer|manager|analyst|intern|consultant|at)\b", re.I)
    project_kw = re.compile(r"\b(project|capstone|thesis|assignment|coursework|mini\s*project)\b", re.I)

    ranges = []
    lines = text.splitlines()
    section = None  # 'experience', 'projects', or None
    for i, raw in enumerate(lines):
        line = (raw or "").strip()
        if not line:
            continue
        # Section detection
        if exp_head.search(line):
            section = 'experience'
        elif proj_head.search(line):
            section = 'projects'

        # Detect date range in a small snippet window
        if 'present' in line.lower() or 'current' in line.lower() or date_pat.search(line):
            window = " ".join((lines[max(0, i-1)] if i-1 >= 0 else "" , line, lines[i+1] if i+1 < len(lines) else ""))
            m = range_pat.search(window)
            if not m:
                continue
            # Filter by context: prefer experience section; otherwise require employment keywords and avoid project keywords
            context = (window or "")
            if section == 'projects':
                continue
            if section == 'experience' or (employment_kw.search(context) and not project_kw.search(context)):
                ranges.append((m.group(1), m.group(2)))

    return {
        "skills": sorted(skills_found),
        "education": education[:10],
        "experience_ranges": ranges[:10],
    }
