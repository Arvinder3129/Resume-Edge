from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes(resume_embeddings, job_embedding, resumes):
    scores = cosine_similarity(resume_embeddings, job_embedding).flatten() * 100
    for i, resume in enumerate(resumes):
        resume["MatchScore"] = round(scores[i], 2)
    return sorted(resumes, key=lambda x: x["MatchScore"], reverse=True)
