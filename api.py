# api.py
from fastapi import FastAPI, File, UploadFile
from resume_parsing import parse_resume_with_llm
from job_matching import calculate_ats_score_with_llm
from database_integration import Candidate, Job, session, save_candidate, save_job, load_embedding_from_db
from faiss_utils import search_faiss, save_faiss_index, add_to_faiss
from embedding_utils import generate_embedding
import numpy as np

app = FastAPI()

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    resume_content = await file.read()
    parsed_data, embedding = parse_resume_with_llm(resume_content)
    
    candidate_name = parsed_data.get("name", "Unknown Candidate")
    
    save_candidate(candidate_name, resume_content, parsed_data, embedding)
    save_faiss_index()
    return {"message": "Resume uploaded successfully", "parsed_data": parsed_data}

@app.post("/post-job/")
async def post_job(job_title: str, job_description: str):
    embedding = generate_embedding(job_description)
    add_to_faiss(embedding)
    save_job(job_title, job_description, embedding)
    save_faiss_index()
    return {"message": "Job posted successfully"}

@app.get("/match-candidates/")
async def match_candidates():
    jobs = session.query(Job).all()
    if not jobs:
        return {"error": "No jobs found in the database"}
    
    results = []
    
    for job in jobs:
        job_embedding = load_embedding_from_db(job.embedding)
        
        # Use FAISS to find top-k candidates
        top_indices = search_faiss(job_embedding, k=10)
        
        matched_candidates = []
        for idx in top_indices:
            # Convert FAISS index to a Python integer
            candidate_id = int(idx) + 1  
            
            candidate = session.query(Candidate).filter_by(id=candidate_id).first()
            if candidate:
                candidate_embedding = load_embedding_from_db(candidate.embedding)
                
                parsed_data = {
                    "skills": candidate.skills.split(),
                    "education": candidate.education.split(),
                    "experience": candidate.experience.split()
                }
                result = calculate_ats_score_with_llm(parsed_data, job.description)
                matched_candidates.append({
                    "candidate_id": candidate.id,
                    "name": candidate.name,
                    "score": result["score"],
                    "explanation": result["explanation"]
                })
        
        results.append({
            "job_id": job.id,
            "job_title": job.title,
            "job_description": job.description,
            "matched_candidates": matched_candidates
        })
    
    return {"results": results}

    
