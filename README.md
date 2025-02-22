# LLM-based-ATS
This project implements an AI-powered Applicant Tracking System (ATS) that automates resume parsing, candidate-job matching, and talent acquisition processes. The system leverages advanced natural language processing (NLP) models, embeddings, and vector databases to streamline recruitment workflows.

## Key features include:

Resume Parsing: Extracts structured data (e.g., name, skills, education, experience) from resumes using state-of-the-art LLMs.
Dynamic Layout Detection: Automatically detects single-column and multi-column resumes and uses the appropriate text extraction method (pdfplumber or PyMuPDF).
Candidate-Job Matching: Evaluates how well candidates match job descriptions using embeddings and similarity search.
FAISS Indexing: Stores and retrieves candidate embeddings efficiently using Facebook's FAISS library with PostgreSQL persistence.
Scalability: Designed to handle large datasets and complex PDF layouts.

### 1. Resume Parsing
Extract key information (name, skills, education, experience) from resumes in PDF format.
Handles both single-column and multi-column layouts dynamically.
Uses pdfplumber for single-column resumes and PyMuPDF for multi-column resumes.
### 2. Embedding Generation
Generates high-quality embeddings for resumes and job descriptions using the sentence-transformers/LaBSE model.
Embeddings are stored in a FAISS index for fast similarity searches.
### 3. Candidate-Job Matching
Matches candidates to jobs based on their skills, education, and experience.
Provides an ATS score (0 to 1) and explanations for each match using a hosted LLM (DeepSeek-R1-Distill-Qwen-32B).
### 4. Database Integration
Saves parsed resumes, job postings, and embeddings to a PostgreSQL database.
Persists the FAISS index in PostgreSQL for seamless reloading.
### 5. RESTful API
Exposes endpoints for uploading resumes, posting jobs, and retrieving candidate-job matches.
Built using FastAPI for high performance and scalability.


### Project Structure

ats_system/
│
├── embedding_utils.py      # Generate embeddings using Hugging Face models
├── faiss_utils.py          # FAISS index management with PostgreSQL persistence
├── resume_parsing.py       # Resume parsing logic with hosted API
├── job_matching.py         # Job matching algorithm with hosted API
├── database_integration.py # Database operations (PostgreSQL)
├── api.py                  # API endpoints
├── requirements.txt        # Dependencies
└── app.py                  # Main application entry point


## Setup Instructions
### 1. Prerequisites
Python 3.8+
PostgreSQL database
Hugging Face API key (for LLM inference)

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Set Environment Variables
HUGGING_FACE_API_KEY=your_hugging_face_api_key
POSTGRES_DB_URL=postgresql://user:password@localhost/dbname

### 4. Initialize PostgreSQL Database
Ensure you have a PostgreSQL database running. Update the connection string in database_integration.py if necessary.

### 5. Run the Application
Start the FastAPI server:
uvicorn app:app --host 0.0.0.0 --port 8000

## How It Works
### 1. Resume Parsing
When a resume is uploaded:

The system detects whether the resume is single-column or multi-column.
Text is extracted using pdfplumber or PyMuPDF.
An LLM parses the text into structured JSON (name, skills, education, experience).
An embedding is generated and added to the FAISS index.
### 2. Job Matching
When a job is posted:

An embedding is generated for the job description.
The system searches the FAISS index for similar candidate embeddings.
An LLM evaluates the match and assigns an ATS score with explanations.






