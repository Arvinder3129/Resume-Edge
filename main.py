from io import StringIO
import os

import pandas as pd
from flask import Flask, jsonify, make_response, render_template, request
from werkzeug.utils import secure_filename

from embeddings import encode_texts
from ranking import rank_resumes
from resume_parser import extract_text_from_resume


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_UPLOAD_SIZE_MB = 32

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def allowed_file(filename):
    return any(filename.lower().endswith(extension) for extension in ALLOWED_EXTENSIONS)


def categorize(score):
    if score >= 70:
        return "Strong"
    if score >= 40:
        return "Moderate"
    return "Weak"


def build_rankings(job_description, uploaded_files):
    resumes = []
    skipped = []

    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename or "")
        if not filename or not allowed_file(filename):
            skipped.append(uploaded_file.filename or "Unnamed file")
            continue

        try:
            text = extract_text_from_resume(uploaded_file, filename)
        except Exception:
            skipped.append(filename)
            continue

        if not text.strip():
            skipped.append(filename)
            continue

        resumes.append(
            {
                "Name": filename,
                "Summary": text,
            }
        )

    if not resumes:
        return [], skipped

    resume_embeddings = encode_texts([resume["Summary"] for resume in resumes])
    job_embedding = encode_texts([job_description])
    ranked = rank_resumes(resume_embeddings, job_embedding, resumes)

    results = []
    for index, resume in enumerate(ranked, start=1):
        score = float(resume["MatchScore"])
        results.append(
            {
                "Rank": index,
                "Name": resume["Name"],
                "MatchScore": score,
                "Category": categorize(score),
            }
        )

    return results, skipped


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/ranker")
def ranker():
    return render_template("ranker.html")


@app.get("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.post("/api/rank")
def api_rank():
    job_description = request.form.get("job_description", "").strip()
    uploaded_files = request.files.getlist("resumes")

    if not job_description:
        return jsonify({"error": "Please enter a job description."}), 400

    if not uploaded_files:
        return jsonify({"error": "Please upload at least one PDF or DOCX resume."}), 400

    results, skipped = build_rankings(job_description, uploaded_files)
    if not results:
        return jsonify({"error": "No readable PDF or DOCX resumes were uploaded.", "skipped": skipped}), 400

    category_counts = pd.DataFrame(results)["Category"].value_counts().to_dict()
    return jsonify(
        {
            "results": results,
            "best_candidate": results[0],
            "category_counts": category_counts,
            "skipped": skipped,
        }
    )


@app.post("/api/download")
def api_download():
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])

    if not results:
        return jsonify({"error": "No ranking results are available to download."}), 400

    df = pd.DataFrame(results)
    expected_columns = ["Rank", "Name", "MatchScore", "Category"]
    for column in expected_columns:
        if column not in df.columns:
            return jsonify({"error": "Ranking results are missing required fields."}), 400

    csv_buffer = StringIO()
    df[expected_columns].to_csv(csv_buffer, index=False)

    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=ranked_resumes.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({"error": f"Uploads must be smaller than {MAX_UPLOAD_SIZE_MB} MB."}), 413


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)



