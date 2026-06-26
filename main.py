from resume_parser import extract_text_from_pdf
from jd_parser import get_job_description
from embeddings import encode_texts
from ranking import rank_resumes

# Example usage
resume_path = "F:/Resume project/saved_model/resumes/New-York-Resume-Template-Creative.pdf"

resumes = [
    {"Name": "NY Resume", "Summary": extract_text_from_pdf(resume_path)}
]

job_description = get_job_description()

resume_embeddings = encode_texts([r["Summary"] for r in resumes])
job_embedding = encode_texts([job_description])

ranked = rank_resumes(resume_embeddings, job_embedding, resumes)

for r in ranked:
    print(r["Name"], r["MatchScore"])
