# Resume Edge

Resume Edge is a modern Flask web application that ranks PDF and DOCX resumes against a job description using sentence-transformer embeddings and cosine similarity.

## Features

- Polished home page at `/`
- Dedicated ranking workspace at `/ranker`
- PDF and DOCX resume parsing
- SentenceTransformer embeddings with cosine similarity ranking
- Strong, Moderate, and Weak match categories
- Chart.js score and category charts
- CSV export through a REST endpoint
- Bootstrap, custom CSS, and JavaScript frontend

## Project structure

```text
Resume Edge/
  app.py
  embeddings.py
  jd_parser.py
  ranking.py
  resume_parser.py
  requirements.txt
  templates/
    index.html
    ranker.html
  static/
    css/
      styles.css
    js/
      app.js
```

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` for the home page or `http://127.0.0.1:5000/ranker` for the ranking workspace.

The first ranking request may take longer while `sentence-transformers` loads `all-MiniLM-L6-v2`.

## REST APIs

### `GET /api/health`

Returns app status.

### `POST /api/rank`

Accepts multipart form data:

- `job_description`: job description text
- `resumes`: one or more PDF or DOCX files

Returns ranked results, the best candidate, category counts, and skipped files.

### `POST /api/download`

Accepts JSON ranking results and returns `ranked_resumes.csv`.
