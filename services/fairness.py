import re
from typing import Dict

# Basic sensitive pattern sets (expandable)
GENDER_PAT = re.compile(r"\b(he|she|him|her|his|hers|mr\.|mrs\.|ms\.)\b", re.I)
AGE_PAT = re.compile(r"\b(\d{2})\s*years?\s*old\b|\bage\s*\d{2}\b", re.I)
MARITAL_PAT = re.compile(r"\b(single|married|divorced|widowed)\b", re.I)
RELIGION_PAT = re.compile(r"\b(hindu|muslim|christian|sikh|buddhist|jain|jewish)\b", re.I)
NATIONALITY_PAT = re.compile(r"\b(indian|american|british|chinese|japanese|german|french|italian|spanish|russian)\b", re.I)
ETHNICITY_PAT = re.compile(r"\b(black|white|asian|hispanic|latino|native american|caucasian)\b", re.I)
CONTACT_PAT = re.compile(r"\b(\+?\d{1,3}[\s-]?)?(\d{3,4}[\s-]?){2,3}\d{3,4}\b|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

REDACTION_TOKEN = "[REDACTED]"


def redact_sensitive(text: str) -> Dict[str, str]:
    if not text:
        return {"redacted": "", "notes": ""}

    notes = []
    out = text
    for name, pat in (
        ("gender", GENDER_PAT),
        ("age", AGE_PAT),
        ("marital", MARITAL_PAT),
        ("religion", RELIGION_PAT),
        ("nationality", NATIONALITY_PAT),
        ("ethnicity", ETHNICITY_PAT),
        ("contact", CONTACT_PAT),
    ):
        if pat.search(out):
            out = pat.sub(REDACTION_TOKEN, out)
            notes.append(name)
    return {"redacted": out, "notes": ",".join(notes)}
