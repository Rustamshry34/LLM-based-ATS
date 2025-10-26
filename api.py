import sentry_sdk
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from resume_parsing import parse_resume_with_llm
from job_matching import calculate_ats_score
from database_integration import save_candidate, save_job, delete_candidate, delete_job, session, Candidate, Job
from chroma_utils import (
    add_to_job_chroma, 
    get_all_jobs_from_chroma,
    delete_resume_from_chroma,
    delete_job_from_chroma
)
from embedding_utils import generate_embedding
import numpy as np
import bleach
import io

sentry_sdk.init(
    dsn="https://78b82319c77e287d108d3702614386dd@o4508931097100288.ingest.de.sentry.io/4508931099000912",  
    traces_sample_rate=1.0, 
    environment="production"  
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the ATS system!"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    
    with sentry_sdk.push_scope() as scope:
        scope.set_context("request", {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
        })
        sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.post("/upload-resume/")
async def upload_resume(name: str, location: str, file: UploadFile = File(...)):


    if not name or name.strip() == "":
        raise HTTPException(status_code=400, detail="Name cannot be empty.")
    if not location or location.strip() == "":
        raise HTTPException(status_code=400, detail="Location cannot be empty.")
    
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF and DOCX files are allowed.")
    
    resume_content = await file.read()
    
    if not resume_content or len(resume_content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    
    max_file_size = 5 * 1024 * 1024  
    if len(resume_content) > max_file_size:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum allowed limit of 5 MB.")
    
    if file.content_type == "application/pdf":
        file_type = "pdf"
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_type = "docx"
    
    parsed_data, _ = parse_resume_with_llm(resume_content, name, location, file_type)
    
    unique_id = parsed_data.get("unique_id")
    save_candidate({
        "name": name,
        "location": location,
        "experience": parsed_data.get("experience"),
        "education": parsed_data.get("education"),
        "skills": parsed_data.get("skills")
    }, unique_id)
    
    return {"message": "Resume uploaded successfully", "parsed_data": parsed_data}

@app.post("/post-job/")
async def post_job(job_title: str, job_description: str):

    if not job_description or job_description.strip() == "":
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    
    max_length = 10_000
    if len(job_description) > max_length:
        raise HTTPException(status_code=400, detail=f"Job description exceeds the maximum allowed length of {max_length} characters.")
    
    sanitized_description = bleach.clean(
        job_description,
        tags=[], 
        attributes={},  
        strip=True  
    )
    
    job_embedding = generate_embedding(sanitized_description)
        
    metadata = {
        "title": job_title,
        "description": sanitized_description
    }
    unique_id = add_to_job_chroma(job_embedding, metadata)

    save_job(job_title, sanitized_description, unique_id)

    return {"message": "Job posted successfully", "unique_id": unique_id}

@app.get("/match-candidates/")
async def match_candidates():
   
    job_ids, job_embeddings, job_metadatas = get_all_jobs_from_chroma()
    
    if not job_ids:
        return {"error": "No jobs found in Databases"}
    
    results = []
    for i, job_embedding in enumerate(job_embeddings):

        job_embedding = np.array(job_embedding)

        matched_candidates = calculate_ats_score(job_embedding)
        results.append({
            "job_id": job_ids[i],
            "job_title": job_metadatas[i].get("title"),
            "job_description": job_metadatas[i].get("description"),
            "matched_candidates": matched_candidates
        })
    
    return {"results": results}


@app.delete("/delete-resume/")
async def delete_resume(unique_id: str):
    
    delete_resume_from_chroma(unique_id)
    
    deleted = delete_candidate(unique_id)
    
    if deleted:
        return {"message": "Resume deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Resume not found")


@app.delete("/delete-job/")
async def delete_job(unique_id: str):
    
    delete_job_from_chroma(unique_id)
    
    deleted = delete_job(unique_id)
    
    if deleted:
        return {"message": "Job deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")        


@app.get("/get-resume-data/")
async def get_resume_data(unique_id: str):
    
    candidate = session.query(Candidate).filter_by(unique_id=unique_id).first()
    if candidate:
        return {
            "name": candidate.name,
            "location": candidate.location,
            "experience": candidate.experience,
            "education": candidate.education,
            "skills": candidate.skills,
        }
    else:
        raise HTTPException(status_code=404, detail="Resume not found")

@app.get("/get-job-data/")
async def get_job_data(unique_id: str):
    
    job = session.query(Job).filter_by(unique_id=unique_id).first()
    if job:
        return {
            "title": job.title,
            "description": job.description
        }
    else:
        raise HTTPException(status_code=404, detail="Job not found")     

        
           

