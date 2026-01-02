import io
import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

from services.extract import extract_text_from_file
from services.nlp import load_nlp, extract_profile
from services.scoring import build_vectorizer, score_candidates
from services.analysis import analyze_profile_vs_job
from services.fairness import redact_sensitive

# Analytics imports
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

NLP = None
VECT = None

# Simple in-memory store to accumulate candidates per lightweight client session
# Structure: { session_id: { 'job_text': str, 'hard_skills': List[str], 'nice_skills': List[str], 'candidates': List[Dict] } }
SESSIONS = {}


def _init_services():
    global NLP, VECT
    if NLP is None:
        NLP = load_nlp()
    if VECT is None:
        VECT = build_vectorizer()


@app.route("/")
def index():
    _init_services()
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    _init_services()
    return render_template("dashboard.html")


@app.route("/api/process", methods=["POST"])
def process():
    _init_services()
    job_text = request.form.get("job_description", "").strip()
    # Redact sensitive attributes from JD before analysis/scoring
    jd_red = redact_sensitive(job_text)
    job_text_redacted = jd_red.get("redacted", job_text)
    hard_skills_raw = request.form.get("hard_skills", "").strip()
    nice_skills_raw = request.form.get("nice_skills", "").strip()
    sess_id = (request.form.get("session_id") or "").strip()

    hard_skills = [s.strip() for s in hard_skills_raw.split(",") if s.strip()] if hard_skills_raw else []
    nice_skills = [s.strip() for s in nice_skills_raw.split(",") if s.strip()] if nice_skills_raw else []

    if not job_text:
        return jsonify({"error": "Job description is required"}), 400

    files = request.files.getlist("resumes")
    if not files and not sess_id:
        return jsonify({"error": "Please upload at least one resume"}), 400

    # Prepare or reset session bucket
    if sess_id:
        bucket = SESSIONS.get(sess_id)
        if bucket is None:
            bucket = {
                'job_text': job_text_redacted,
                'hard_skills': hard_skills,
                'nice_skills': nice_skills,
                'candidates': []
            }
            SESSIONS[sess_id] = bucket
        else:
            # If JD or skills changed significantly, reset accumulation to avoid mixing contexts
            if (
                bucket.get('job_text') != job_text_redacted or
                bucket.get('hard_skills') != hard_skills or
                bucket.get('nice_skills') != nice_skills
            ):
                bucket['job_text'] = job_text_redacted
                bucket['hard_skills'] = hard_skills
                bucket['nice_skills'] = nice_skills
                bucket['candidates'] = []
    else:
        bucket = None

    candidates = [] if bucket is None else list(bucket['candidates'])

    for f in files:
        filename = f.filename
        try:
            content = f.read()
            text = extract_text_from_file(filename, content)
            # Redact sensitive attributes before scoring/vectorizing
            res_red = redact_sensitive(text)
            text_redacted = res_red.get("redacted", text)

            prof = extract_profile(NLP, text_redacted)
            analysis = analyze_profile_vs_job(prof, job_text_redacted, hard_skills, nice_skills, candidate_text=text_redacted)
            new_entry = {
                "filename": filename,
                "raw_text": text[:20000],
                "raw_text_redacted": text_redacted[:20000],
                "redaction_notes": res_red.get("notes", ""),
                **prof,
                **analysis,
            }
            # De-duplicate by filename: replace existing with the same filename
            replaced = False
            for idx, c in enumerate(candidates):
                if (c.get("filename") or "") == filename:
                    candidates[idx] = new_entry
                    replaced = True
                    break
            if not replaced:
                candidates.append(new_entry)
        except Exception as e:
            candidates.append({
                "filename": filename,
                "error": str(e)
            })

    ranked = score_candidates(VECT, job_text_redacted, candidates, hard_skills, nice_skills)

    # Persist back into session bucket if present
    if bucket is not None:
        bucket['candidates'] = candidates

    # Store in session-like memory for CSV download
    request.environ["ranked_results"] = ranked

    return jsonify({
        "results": ranked
    })


@app.route("/api/export", methods=["POST"]) 
def export_csv():
    # Results are not persisted; rebuild from request payload to keep simple
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])
    si = io.StringIO()
    writer = csv.writer(si)
    headers = [
        "filename", "overall_score", "keyword_score", "semantic_score", "hard_skill_coverage",
        "nice_skill_coverage", "missing_hard_skills", "gaps", "flags"
    ]
    writer.writerow(headers)
    for r in results:
        writer.writerow([
            r.get("filename"),
            f"{r.get('overall_score', 0):.4f}",
            f"{r.get('keyword_score', 0):.4f}",
            f"{r.get('semantic_score', 0):.4f}",
            f"{r.get('hard_skill_coverage', 0):.2f}",
            f"{r.get('nice_skill_coverage', 0):.2f}",
            "; ".join(r.get("missing_hard_skills", [])),
            "; ".join([f"{g['start']} - {g['end']}" for g in r.get("gaps", [])]),
            "; ".join(r.get("flags", [])),
        ])
    mem = io.BytesIO(si.getvalue().encode("utf-8"))
    fname = f"ranked_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=fname)


@app.route("/api/analytics", methods=["POST"]) 
def analytics():
    _init_services()
    job_text = request.form.get("job_description", "").strip()
    if not job_text:
        return jsonify({"error": "Job description is required"}), 400

    # Redact JD for fairness
    jd_red = redact_sensitive(job_text)
    job_text_redacted = jd_red.get("redacted", job_text)

    hard_skills_raw = request.form.get("hard_skills", "").strip()
    nice_skills_raw = request.form.get("nice_skills", "").strip()
    sess_id = (request.form.get("session_id") or "").strip()

    hard_skills = [s.strip() for s in hard_skills_raw.split(",") if s.strip()] if hard_skills_raw else []
    nice_skills = [s.strip() for s in nice_skills_raw.split(",") if s.strip()] if nice_skills_raw else []

    files = request.files.getlist("resumes")
    if not files and not sess_id:
        return jsonify({"error": "Please upload at least one resume"}), 400

    # Build candidate profiles first (with redaction) so we can attach analytics to each
    # Session accumulation for analytics as well
    if sess_id:
        bucket = SESSIONS.get(sess_id)
        if bucket is None:
            bucket = {
                'job_text': job_text_redacted,
                'hard_skills': hard_skills,
                'nice_skills': nice_skills,
                'candidates': []
            }
            SESSIONS[sess_id] = bucket
        else:
            if (
                bucket.get('job_text') != job_text_redacted or
                bucket.get('hard_skills') != hard_skills or
                bucket.get('nice_skills') != nice_skills
            ):
                bucket['job_text'] = job_text_redacted
                bucket['hard_skills'] = hard_skills
                bucket['nice_skills'] = nice_skills
                bucket['candidates'] = []
        raw_candidates = list(bucket['candidates'])
    else:
        raw_candidates = []

    for f in files:
        filename = f.filename
        try:
            content = f.read()
            text = extract_text_from_file(filename, content)
            res_red = redact_sensitive(text)
            text_redacted = res_red.get("redacted", text)
            prof = extract_profile(NLP, text_redacted)
            analysis = analyze_profile_vs_job(prof, job_text_redacted, hard_skills, nice_skills, candidate_text=text_redacted)
            new_entry = {
                "filename": filename,
                "raw_text": text[:20000],
                "raw_text_redacted": text_redacted[:20000],
                "redaction_notes": res_red.get("notes", ""),
                **prof,
                **analysis,
            }
            # replace or append
            replaced = False
            for i, c in enumerate(raw_candidates):
                if (c.get("filename") or "") == filename:
                    raw_candidates[i] = new_entry
                    replaced = True
                    break
            if not replaced:
                raw_candidates.append(new_entry)
        except Exception as e:
            raw_candidates.append({
                "filename": filename,
                "error": str(e)
            })

    if sess_id:
        SESSIONS[sess_id]['candidates'] = raw_candidates

    n = len(raw_candidates)

    # Vectorize on redacted texts for fairness
    docs = [job_text_redacted] + [c.get("raw_text_redacted") or c.get("raw_text", "") for c in raw_candidates]
    try:
        X = VECT.fit_transform(docs)
        cand_X = X[1:]
    except Exception:
        cand_X = None

    # PCA 2D projection
    coords = [[0.0, 0.0] for _ in range(n)]
    if cand_X is not None and n > 0:
        try:
            dense = cand_X.toarray()
            if n >= 2 and dense.shape[1] >= 2:
                pca = PCA(n_components=2, random_state=42)
                XY = pca.fit_transform(dense)
                coords = XY.tolist()
            else:
                coords = [[0.0, 0.0] for _ in range(n)]
        except Exception:
            coords = [[0.0, 0.0] for _ in range(n)]

    # KMeans clustering with adaptive K
    labels = [0 for _ in range(n)]
    if cand_X is not None and n >= 2:
        try:
            dense = cand_X.toarray()
            k = min(6, max(2, int(round(n ** 0.5))))
            k = min(k, n)  # safety
            if k >= 1:
                km = KMeans(n_clusters=k, n_init=10, random_state=42)
                km.fit(dense)
                labels = list(map(int, km.labels_.tolist()))
        except Exception:
            labels = [0 for _ in range(n)]

    # Nearest neighbors (Top-5) by cosine similarity
    neighbors_all = [[] for _ in range(n)]
    if cand_X is not None and n >= 2:
        try:
            sim = cosine_similarity(cand_X)
            for i in range(n):
                scores = [(j, float(sim[i, j])) for j in range(n) if j != i]
                scores.sort(key=lambda t: t[1], reverse=True)
                top5 = scores[:5]
                neighbors_all[i] = [
                    {"filename": raw_candidates[j].get("filename"), "sim": s}
                    for j, s in top5
                ]
        except Exception:
            neighbors_all = [[] for _ in range(n)]

    # Attach analytics to candidate dicts before scoring so they carry through
    for i, c in enumerate(raw_candidates):
        c["pca"] = {"x": float(coords[i][0]), "y": float(coords[i][1])} if i < len(coords) else {"x": 0.0, "y": 0.0}
        c["cluster_id"] = int(labels[i]) if i < len(labels) else 0
        c["neighbors"] = neighbors_all[i] if i < len(neighbors_all) else []

    # Score and rank (uses redacted JD and candidates)
    ranked = score_candidates(VECT, job_text_redacted, raw_candidates, hard_skills, nice_skills)

    # Predictive hiring success score (transparent heuristic)
    for r in ranked:
        overall = float(r.get("overall_score", 0))
        trend = float(r.get("trend_score", 0))
        hard_cov = float(r.get("hard_skill_coverage", 0))
        semantic = float(r.get("semantic_score", 0))
        penalties = 0.0
        if r.get("gaps"): penalties += 0.30
        if r.get("overlaps"): penalties += 0.20
        if "potential_exaggeration_detected" in (r.get("flags") or []): penalties += 0.20
        success = 0.55*overall + 0.15*trend + 0.15*hard_cov + 0.10*semantic - 0.05*penalties
        success = max(0.0, min(1.0, float(success)))
        r["success_score"] = success
        r["success_explain"] = [
            f"overall*0.55={0.55*overall:.3f}",
            f"trend*0.15={0.15*trend:.3f}",
            f"hard_cov*0.15={0.15*hard_cov:.3f}",
            f"semantic*0.10={0.10*semantic:.3f}",
            f"penalty*0.05={0.05*penalties:.3f}"
        ]

    return jsonify({"results": ranked})


if __name__ == "__main__":
    _init_services()
    app.run(debug=True)
