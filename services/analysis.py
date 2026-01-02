from typing import Dict, List, Optional, Tuple
import re
from dateutil import parser as dateparser
from datetime import datetime, timedelta

# ---------- Date utilities ----------

def _parse_date(token: str):
    token = token.strip().replace('\u2013', '-').replace('\u2014', '-').replace('to', '-')
    try:
        return dateparser.parse(token, default=datetime(2000, 1, 1), fuzzy=True)
    except Exception:
        return None


def _normalize_range(start: str, end: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    s = _parse_date(start)
    e = None if str(end).strip().lower() in ("present", "current") else _parse_date(end)
    return s, e


def _normalize_ranges(ranges: List[Tuple[str, str]]) -> List[Tuple[datetime, datetime]]:
    # Convert to (start_dt, end_dt), replacing None end with now
    now = datetime.now()
    norm: List[Tuple[datetime, datetime]] = []
    for r in ranges:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            s, e = _normalize_range(str(r[0]), str(r[1]))
            if s:
                norm.append((s, (e or now)))
    # Filter invalid
    norm = [(s, e) for s, e in norm if s <= e]
    # Sort by start asc
    norm.sort(key=lambda x: x[0])
    return norm


def _months_between(a: datetime, b: datetime) -> float:
    # Approximate month difference including partial months
    if b < a:
        a, b = b, a
    years = b.year - a.year
    months = b.month - a.month
    days = b.day - a.day
    total_months = years * 12 + months + (days / 30.0)
    return max(0.0, total_months)


def _filter_short_intervals(norm: List[Tuple[datetime, datetime]], min_months: float = 2.0) -> List[Tuple[datetime, datetime]]:
    # Remove intervals shorter than a small threshold to avoid treating short project/course durations as jobs
    if not norm:
        return []
    return [(s, e) for (s, e) in norm if _months_between(s, e) >= min_months]


def _merge_intervals(norm: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    if not norm:
        return []
    merged: List[Tuple[datetime, datetime]] = []
    cur_s, cur_e = norm[0]
    for i in range(1, len(norm)):
        s, e = norm[i]
        if s <= cur_e:  # overlap/adjacent
            if e > cur_e:
                cur_e = e
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged


def _calc_total_experience_months(norm: List[Tuple[datetime, datetime]]) -> float:
    merged = _merge_intervals(norm)
    return sum(_months_between(s, e) for s, e in merged)


def _find_gaps(norm: List[Tuple[datetime, datetime]]):
    # Find gaps greater than ~3 months between consecutive intervals (sorted)
    gaps = []
    if len(norm) < 2:
        return gaps
    for i in range(1, len(norm)):
        prev_end = norm[i-1][1]
        curr_start = norm[i][0]
        delta = (curr_start - prev_end).days
        if delta > 92:  # > ~3 months
            gaps.append({
                "start": prev_end.date().isoformat(),
                "end": curr_start.date().isoformat(),
                "days": delta
            })
    return gaps


def _detect_overlaps(norm: List[Tuple[datetime, datetime]]):
    # Overlap if current start < previous end beyond a tolerance (30 days)
    overlaps = []
    if len(norm) < 2:
        return overlaps
    tol = timedelta(days=30)
    for i in range(1, len(norm)):
        prev_s, prev_e = norm[i-1]
        cur_s, cur_e = norm[i]
        if cur_s + tol < prev_e:
            start = cur_s
            end = min(prev_e, cur_e)
            overlaps.append({
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "days": (end - start).days
            })
    return overlaps

# ---------- Text heuristics ----------
SUPERLATIVES = [
    "world-class", "world class", "best", "unparalleled", "unmatched", "exceptional",
    "revolutionary", "groundbreaking", "state-of-the-art", "cutting-edge", "cutting edge"
]
IMPROVEMENT_WORDS = [
    "increase", "increased", "increaseed", "boost", "boosted", "improve", "improved", "reduce", "reduced",
    "grew", "grow", "accelerate", "accelerated", "decrease", "decreased", "cut"
]

SENSITIVE_PAT = re.compile(r"\b(\d{2}\s*years?\s*old|male\b|female\b|married\b|single\b)\b", re.I)

PCT_PAT = re.compile(r"\b(\d{1,3})\s*%|\b(\d{1,3})\s*percent\b", re.I)
MULT_X_PAT = re.compile(r"\b(\d{1,3})\s*[xX]\b")
YEARS_STATED_PAT = re.compile(
    r"(?:(?:over|more than|approximately|approx|~)\s*)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs)\b",
    re.I
)
YEARS_RANGE_PAT = re.compile(r"\b(\d+(?:\.\d+)?)\s*[-to]{1,3}\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs)\b", re.I)


def _extract_stated_years(text: str) -> Optional[float]:
    if not text:
        return None
    # range like 3-5 years -> midpoint
    m = YEARS_RANGE_PAT.search(text)
    if m:
        try:
            a = float(m.group(1))
            b = float(m.group(2))
            return (a + b) / 2.0
        except Exception:
            pass
    # single like 5+ years
    m = YEARS_STATED_PAT.search(text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None


def _metric_anomaly_heuristics(text: str) -> List[str]:
    reasons = []
    if not text:
        return reasons
    t = text.lower()

    # Percentages
    pct_vals = []
    for m in PCT_PAT.finditer(t):
        v = m.group(1) or m.group(2)
        try:
            v = int(v)
            pct_vals.append(v)
        except Exception:
            pass
    extreme_pct = [v for v in pct_vals if v >= 300]
    if extreme_pct:
        reasons.append(f"extreme_percent_claims: {sorted(set(extreme_pct))}%")

    # Multipliers
    mult_vals = []
    for m in MULT_X_PAT.finditer(t):
        try:
            mult_vals.append(int(m.group(1)))
        except Exception:
            pass
    extreme_mult = [v for v in mult_vals if v >= 10]
    if extreme_mult:
        reasons.append(f"extreme_multiplier_claims: {sorted(set(extreme_mult))}x")

    # Superlatives without metrics
    sup_count = sum(t.count(s) for s in SUPERLATIVES)
    if sup_count >= 5 and not (pct_vals or mult_vals):
        reasons.append("many_superlatives_without_metrics")

    # Improvement words without timeframe
    if any(w in t for w in IMPROVEMENT_WORDS) and not re.search(r"\b(months?|years?|weeks?)\b", t):
        reasons.append("claims_without_timeframe")

    return reasons


# ---------- Main analysis ----------

def analyze_profile_vs_job(
    profile: Dict,
    job_text: str,
    hard_skills: List[str],
    nice_skills: List[str],
    candidate_text: Optional[str] = None,
) -> Dict:
    # Enrich profile deterministically (skills synonyms, contacts/certs, extra ranges, education normalization)
    profile = _enrich_profile(profile, candidate_text or "")
    # Normalize date ranges
    ranges = profile.get("experience_ranges", [])
    norm = _normalize_ranges(ranges)
    # Filter out very short spans (likely projects/coursework) before computing gaps/overlaps
    norm = _filter_short_intervals(norm, min_months=2.0)

    # Gaps and overlaps
    gaps = _find_gaps(norm)
    overlaps = _detect_overlaps(norm)

    # Total experience
    total_months = _calc_total_experience_months(norm)
    total_years = round(total_months / 12.0, 2)

    # Duration plausibility (compare with stated years if present)
    stated_years = _extract_stated_years(candidate_text or "")
    duration_inconsistency = False
    if stated_years is not None:
        if abs(total_years - stated_years) > 1.5:  # > 18 months diff
            duration_inconsistency = True

    # Duplicate claims heuristic (keep simple from earlier)
    lines = [l for l in profile.get("education", [])]
    dups = _detect_duplicates(lines)

    flags = []
    if gaps:
        flags.append("employment_gaps_detected")
    if overlaps:
        flags.append("overlapping_roles_detected")
    if dups:
        flags.append("possible_duplicate_claims")

    # Sensitive info redaction note for JD
    if SENSITIVE_PAT.search(job_text or ""):
        flags.append("remove_sensitive_attributes_from_job_description")

    # Missing skills vs hard skills (after enrichment)
    cand_skills = set(s.lower() for s in profile.get("skills", []))
    hard_lower = set(s.lower() for s in hard_skills)
    missing = sorted([s for s in hard_lower if s not in cand_skills])

    # Metric anomaly heuristics (resume text)
    anomaly_reasons: List[str] = []
    if candidate_text:
        anomaly_reasons = _metric_anomaly_heuristics(candidate_text)
        if duration_inconsistency:
            anomaly_reasons.append("duration_inconsistency_vs_stated_years")
    else:
        # If resume text not provided, we can still flag duration inconsistency based on ranges only (if extreme)
        if total_years < 0.25:  # suspiciously low total experience
            anomaly_reasons.append("very_low_total_experience_in_ranges")

    if anomaly_reasons:
        flags.append("potential_exaggeration_detected")

    return {
        "gaps": gaps,
        "overlaps": overlaps,
        "total_experience_years": total_years,
        "stated_years": stated_years,
        "flags": flags,
        "anomaly_reasons": anomaly_reasons,
        "missing_hard_skills": missing,
        # Pass-through enriched fields for UI/future use
        "contacts": profile.get("contacts", {}),
        "certifications": profile.get("certifications", [])[:10],
        "education_normalized": profile.get("education_normalized", [])[:10],
    }


# ---------- Enrichment (deterministic NLP without ML) ----------

SKILL_SYNONYMS = {
    "js": "javascript", "nodejs": "node", "ts": "typescript", "tf": "tensorflow",
    "scikit learn": "scikit-learn", "nltk": "nlp", "natural language processing": "nlp",
    "ml": "machine learning", "dl": "deep learning",
}

MULTI_SKILLS = [
    "machine learning", "data science", "deep learning", "natural language processing",
    "computer vision", "project management", "data analysis", "web development",
    "object oriented programming", "rest api", "microservices"
]

EMPLOYMENT_KW = re.compile(r"\b(employer|company|role|position|engineer|developer|manager|analyst|intern|consultant|at)\b", re.I)
PROJECT_KW = re.compile(r"\b(project|capstone|thesis|assignment|coursework|mini\s*project)\b", re.I)


def _enrich_profile(profile: Dict, text: str) -> Dict:
    t = (text or "")
    lowered = t.lower()
    # Skills synonyms & multi-phrases
    sk = set(s.lower() for s in profile.get("skills", []))
    # add multi-phrase hits
    for ph in MULTI_SKILLS:
        if ph in lowered:
            sk.add(ph)
    # expand synonyms if raw mention exists in text
    tokens = re.split(r"[^a-zA-Z0-9+#\.\-]", lowered)
    for tok in tokens:
        if not tok:
            continue
        canon = SKILL_SYNONYMS.get(tok)
        if canon:
            sk.add(canon)
    profile["skills"] = sorted(sk)

    # Education normalization (lightweight on raw lines if available)
    edu_norm: List[Dict[str, str]] = []
    DEG_MAP = [
        (re.compile(r"\b(ph\.?d|doctor(?:ate)?|dphil)\b", re.I), "phd"),
        (re.compile(r"\b(m\.?tech|ms|m\.sc|master|mba)\b", re.I), "masters"),
        (re.compile(r"\b(b\.?tech|b\.?e\.?|b\.sc|bachelor)\b", re.I), "bachelor"),
        (re.compile(r"\b(diploma|associate)\b", re.I), "diploma"),
    ]
    for l in profile.get("education", []):
        norm = None
        for pat, lvl in DEG_MAP:
            if pat.search(l):
                norm = lvl; break
        if norm:
            edu_norm.append({"raw": l, "level": norm})
    profile["education_normalized"] = edu_norm

    # Certifications detection
    certs_pat = [
        r"aws\s*(developer|architect|solutions|practitioner)", r"azure\s*(fundamentals|developer|architect)",
        r"gcp\s*(professional|associate)", r"pmp\b", r"scrum\s*(master|product\s*owner)", r"oca|ocp|ocajp|ocpjp",
        r"rhce|rhcsa", r"cka|ckad", r"cissp|security\+", r"itil\b"
    ]
    certs = []
    for pat in certs_pat:
        for m in re.finditer(pat, lowered, re.I):
            val = (m.group(0) or "").strip()
            if val and val not in certs:
                certs.append(val)
    profile["certifications"] = certs[:10]

    # Contacts extraction
    contacts: Dict[str, List[str]] = {}
    m_email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", t, re.I)
    if m_email:
        contacts["email"] = m_email.group(0)
    m_phone = re.search(r"\+?\d[\d\s().-]{8,}\d", t)
    if m_phone:
        contacts["phone"] = m_phone.group(0)
    links = re.findall(r"https?://[^\s)]+", t)
    if links:
        contacts["links"] = links[:5]
    profile["contacts"] = contacts

    # Supplemental experience ranges: support numeric/year-only if accompanied by employment context and not projects
    extra_ranges: List[Tuple[str, str]] = []
    lines = t.splitlines()
    range_num = r"\d{1,2}[\/\-]\d{4}"
    range_year = r"\b\d{4}\b"
    sep = r"[\u2013\-–—to]+"
    pat_num = re.compile(rf"({range_num})\s*{sep}\s*({range_num}|present|current)", re.I)
    pat_year = re.compile(rf"({range_year})\s*{sep}\s*({range_year}|present|current)", re.I)
    for i, raw in enumerate(lines):
        l = (raw or "").strip()
        if not l:
            continue
        if PROJECT_KW.search(l):
            continue
        ctx = " ".join(lines[max(0, i-1): i+2])
        if not EMPLOYMENT_KW.search(ctx):
            continue
        m = pat_num.search(l) or pat_year.search(l)
        if m:
            extra_ranges.append((m.group(1), m.group(2)))
    if extra_ranges:
        exist = set(tuple(r) for r in profile.get("experience_ranges", []))
        for r in extra_ranges:
            if tuple(r) not in exist:
                profile.setdefault("experience_ranges", []).append(r)

    return profile


# ---------- Simple duplicate detection (kept from previous) ----------

def _detect_duplicates(lines: List[str]) -> List[str]:
    seen = set()
    dups = []
    for l in lines:
        k = (l or "").strip().lower()
        if not k:
            continue
        if k in seen and len(k) > 15:
            dups.append((l or "").strip())
        seen.add(k)
    return dups[:5]
