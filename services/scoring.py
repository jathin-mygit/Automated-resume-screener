from typing import List, Dict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import json

# Optional trends override at data/skill_trends.json
TRENDS_PATH = Path(__file__).resolve().parent.parent / "data" / "skill_trends.json"


def _load_trend_weights() -> Dict[str, float]:
    # Default in-demand / future-ready skills with weights (0..1)
    defaults = {
        # Cloud & DevOps
        "aws": 1.0, "azure": 0.9, "gcp": 0.9, "docker": 0.9, "kubernetes": 1.0,
        "terraform": 0.9, "ci/cd": 0.8, "github actions": 0.6, "gitlab ci": 0.6,
        # Data & Streaming
        "kafka": 0.9, "airflow": 0.8, "spark": 0.9, "databricks": 0.9, "snowflake": 0.9, "dbt": 0.8,
        # ML & MLOps
        "pytorch": 0.9, "tensorflow": 0.9, "transformers": 0.9, "mlops": 0.9, "mlflow": 0.8,
        "llm": 1.0, "langchain": 0.8, "vector db": 0.7, "faiss": 0.7, "weaviate": 0.7, "pinecone": 0.7,
        # Backend & Languages
        "go": 0.8, "golang": 0.8, "rust": 0.9, "fastapi": 0.8, "grpc": 0.8,
        # Frontend
        "typescript": 0.9, "react": 0.8, "next.js": 0.8, "nextjs": 0.8,
        # Observability & Reliability
        "opentelemetry": 0.8, "prometheus": 0.7, "grafana": 0.7,
        # Infra-as-Code & Security
        "ansible": 0.7, "vault": 0.6, "k9s": 0.4,
    }
    if TRENDS_PATH.exists():
        try:
            data = json.loads(TRENDS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged = {**defaults}
                for k, v in data.items():
                    try:
                        merged[str(k).lower()] = float(v)
                    except Exception:
                        continue
                return merged
        except Exception:
            return {k.lower(): v for k, v in defaults.items()}
    return {k.lower(): v for k, v in defaults.items()}


TREND_WEIGHTS = _load_trend_weights()
TREND_TOTAL = max(1e-6, float(sum(TREND_WEIGHTS.values())))


def build_vectorizer():
    return TfidfVectorizer(stop_words='english', lowercase=True, max_features=5000)


def _lower_set(items):
    return {str(s).lower() for s in items}


def _detect_trend_skills(text_lower: str, cand_skills_lower: set) -> (List[str], float):
    matched = []
    score_sum = 0.0
    for skill, weight in TREND_WEIGHTS.items():
        if skill in text_lower or skill in cand_skills_lower:
            matched.append(skill)
            score_sum += float(weight)
    trend_score = min(1.0, score_sum / TREND_TOTAL) if TREND_TOTAL > 0 else 0.0
    return sorted(matched), float(trend_score)


def score_candidates(vectorizer, job_text: str, candidates: List[Dict], hard_skills: List[str], nice_skills: List[str]):
    # Prepare documents for semantic similarity
    jd_lower = (job_text or "").lower()
    # JD-aware emphasis rules (deterministic)
    JD_CERT_KEYS = [r"aws", r"azure", r"gcp", r"certified", r"cissp", r"pmp", r"cka", r"ckad", r"rhce", r"oci|oracle"]
    JD_COMPLIANCE_KEYS = [r"pci", r"hipaa", r"sox|soc\s*2", r"iso\s*27001", r"gdpr"]
    jd_cert_focus = any(re.search(k, jd_lower) for k in JD_CERT_KEYS)
    jd_compliance_focus = any(re.search(k, jd_lower) for k in JD_COMPLIANCE_KEYS)
    jd_tags = []
    if jd_cert_focus: jd_tags.append("jd_emphasis:certifications")
    if jd_compliance_focus: jd_tags.append("jd_emphasis:compliance")
    docs = [job_text] + [c.get("raw_text_redacted") or c.get("raw_text", "") for c in candidates]
    try:
        X = vectorizer.fit_transform(docs)
        job_vec = X[0:1]
        cand_vecs = X[1:]
        semantic_scores = cosine_similarity(job_vec, cand_vecs).ravel()
    except Exception:
        semantic_scores = np.zeros(len(candidates))

    hard_lower = _lower_set(hard_skills)
    nice_lower = _lower_set(nice_skills)

    results = []
    for i, cand in enumerate(candidates):
        text_source = cand.get("raw_text_redacted") or cand.get("raw_text", "")
        text_lower = text_source.lower()
        cand_skills = _lower_set(cand.get("skills", []))

        # Keyword scores: presence counts
        hard_hits = sum(1 for s in hard_lower if s in text_lower or s in cand_skills)
        nice_hits = sum(1 for s in nice_lower if s in text_lower or s in cand_skills)

        hard_cov = (hard_hits / max(1, len(hard_lower))) if hard_lower else 0.0
        nice_cov = (nice_hits / max(1, len(nice_lower))) if nice_lower else 0.0

        keyword_score = 0.7 * hard_cov + 0.3 * nice_cov

        semantic_score = float(semantic_scores[i]) if i < len(semantic_scores) else 0.0

        # Trend skills detection and score
        trend_skills, trend_score = _detect_trend_skills(text_lower, cand_skills)

        # Base overall from core signals
        base_overall = 0.5 * keyword_score + 0.35 * semantic_score + 0.15 * trend_score

        # Deterministic bonuses (no ML)
        # Certifications bonus: up to +0.06 (or +0.08 if JD emphasizes certs)
        certs = cand.get("certifications") or []
        cert_cap = 0.08 if jd_cert_focus else 0.06
        cert_bonus = min(cert_cap, 0.03 * len(certs))
        # Education bonus based on highest normalized level
        edu_norm = cand.get("education_normalized") or []
        highest = ""
        levels = {"phd": 0.06, "masters": 0.03, "bachelor": 0.01, "diploma": 0.0}
        for e in edu_norm:
            lvl = str(e.get("level", "")).lower()
            if lvl in ("phd", "masters", "bachelor", "diploma"):
                if not highest or levels.get(lvl, 0.0) > levels.get(highest, 0.0):
                    highest = lvl
        edu_bonus = levels.get(highest, 0.0)
        # Contact completeness bonus: up to +0.02
        contacts = cand.get("contacts") or {}
        has_email = bool(contacts.get("email"))
        has_phone = bool(contacts.get("phone"))
        has_links = bool(contacts.get("links")) and len(contacts.get("links", [])) > 0
        contact_bonus = 0.0
        contact_bonus += 0.007 if has_email else 0.0
        contact_bonus += 0.007 if has_phone else 0.0
        contact_bonus += 0.006 if has_links else 0.0
        contact_bonus = min(0.02, contact_bonus)

        # Penalize certain flags (small, transparent)
        flags = cand.get("flags") or []
        penalty_sum = 0.0
        PEN = {
            "employment_gaps_detected": 0.05,
            "overlapping_roles_detected": 0.03,
            "possible_duplicate_claims": 0.02,
            "potential_exaggeration_detected": 0.04,
        }
        for f in flags:
            if f in PEN:
                penalty_sum += PEN[f]
        penalty_sum = min(0.10, penalty_sum)

        # Final overall score with bonuses/penalties
        overall = base_overall + cert_bonus + edu_bonus + contact_bonus - penalty_sum
        overall = float(max(0.0, min(1.0, overall)))

        missing_hard = sorted([s for s in hard_lower if s not in text_lower and s not in cand_skills])

        # Multi-source consistency checks
        # Consistent if skill is both in structured skills and present in text
        consistent_hits = sum(1 for s in hard_lower if (s in cand_skills and s in text_lower))
        total_considered = max(1, len(hard_lower))
        consistency = consistent_hits / total_considered
        consistency_bonus = 0.0
        if consistency >= 0.5:
            consistency_bonus = 0.02
        elif consistency >= 0.25:
            consistency_bonus = 0.01
        # Cap combined bonus by residual margin to 1.0
        if overall + consistency_bonus > 1.0:
            consistency_bonus = max(0.0, 1.0 - overall)
        overall = float(max(0.0, min(1.0, overall + consistency_bonus)))

        # Confidence heuristic: agreement + completeness - penalties
        agreement = 1.0 - min(1.0, abs(keyword_score - semantic_score))
        confidence = 0.5 * agreement + 0.25 * float(hard_cov) + 0.25 * (1.0 - min(1.0, penalty_sum))
        confidence = float(max(0.0, min(1.0, confidence)))

        # Structured risk score (separate from overall)
        risk = 0.0
        risk_reasons = []
        if flags:
            if "employment_gaps_detected" in flags:
                risk += 0.25; risk_reasons.append("employment_gaps")
            if "overlapping_roles_detected" in flags:
                risk += 0.2; risk_reasons.append("overlapping_roles")
            if "possible_duplicate_claims" in flags:
                risk += 0.15; risk_reasons.append("duplicate_claims")
            if "potential_exaggeration_detected" in flags:
                risk += 0.2; risk_reasons.append("exaggeration")
        if len(cand.get("experience_ranges", []) or []) == 0:
            risk += 0.15; risk_reasons.append("no_experience_dates")
        if not has_email or not has_phone:
            risk += 0.1; risk_reasons.append("missing_contact")
        risk = float(max(0.0, min(1.0, risk)))
        if risk >= 0.6:
            risk_label = "High"
        elif risk >= 0.3:
            risk_label = "Medium"
        else:
            risk_label = "Low"

        # Transparent explanation of overall
        explain = [
            f"keyword*0.50={0.50*keyword_score:.3f}",
            f"semantic*0.35={0.35*semantic_score:.3f}",
            f"trend*0.15={0.15*trend_score:.3f}",
        ]
        if cert_bonus > 1e-6:
            explain.append(f"cert_bonus+={cert_bonus:.3f}")
        if edu_bonus > 1e-6:
            explain.append(f"edu_bonus+={edu_bonus:.3f}")
        if contact_bonus > 1e-6:
            explain.append(f"contact_bonus+={contact_bonus:.3f}")
        if penalty_sum > 1e-6:
            explain.append(f"penalties-={penalty_sum:.3f}")
        if consistency_bonus > 1e-6:
            explain.append(f"consistency_bonus+={consistency_bonus:.3f}")
        explain.extend(jd_tags)

        enriched = {
            **cand,
            "keyword_score": float(keyword_score),
            "semantic_score": float(semantic_score),
            "trend_score": float(trend_score),
            "trend_skills": trend_skills,
            "overall_score": overall,
            "hard_skill_coverage": round(hard_cov, 3),
            "nice_skill_coverage": round(nice_cov, 3),
            "missing_hard_skills": missing_hard,
            "confidence": confidence,
            "overall_explain": explain,
            "risk_score": risk,
            "risk_label": risk_label,
            "risk_reasons": risk_reasons,
            "consistency": round(consistency, 3),
        }
        results.append(enriched)

    # Sort descending by overall score, then minimize flags and gaps
    results.sort(key=lambda x: (x.get("overall_score", 0), -len(x.get("flags", [])), -len(x.get("gaps", []))), reverse=True)
    return results
