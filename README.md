# AI-Powered-ATS
This project implements an AI-powered Applicant Tracking System (ATS) that automates resume parsing, candidate-job matching, and talent acquisition processes. The system leverages advanced natural language processing (NLP) models, embeddings, and vector databases to streamline recruitment workflows.

[![Deploy ATS to AWS](https://github.com/Rustamshry34/LLM-based-ATS/actions/workflows/deploy.yml/badge.svg)](https://github.com/Rustamshry34/LLM-based-ATS/actions/workflows/deploy.yml)

## Key features include:

Resume Parsing: Extracts structured data (e.g., name, skills, education, experience) from resumes using LlamaIndex.

Candidate-Job Matching: Evaluates how well candidates match job descriptions using embeddings and similarity search.

Vector Database: Stores and retrieves candidate embeddings efficiently using the ChromaDB library with PostgreSQL persistence.

Scalability: Designed to handle large datasets and complex PDF layouts.

### 1. Resume Parsing
Extract key information (name, skills, education, experience) from resumes in PDF format.
Handles both single-column and multi-column layouts dynamically.
Uses LlamaParsa and LlamaCloud for resume parsing.
### 2. Embedding Generation
Generates high-quality embeddings for resumes and job descriptions using the sentence-transformers/MiniLM-L12-v2 model.
Embeddings are stored in a Vector Database index for fast similarity searches.
### 3. Candidate-Job Matching
Matches candidates to jobs based on their skills, education, and experience.
### 4. Database Integration
Saves parsed resumes, job postings and embeddings to a PostgreSQL database and ChromaDB.
### 5. RESTful API
Exposes endpoints for uploading resumes, posting jobs, deleting job and resume information, and retrieving candidate-job matches.
Built using FastAPI for high performance and scalability.


## Setup Instructions
### 1. Prerequisites
Python 3.8+
PostgreSQL database
LLamaIndex API key (for resume parsing)

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Set Environment Variables
os.environ["LLAMA_CLOUD_API_KEY"] = ""
POSTGRES_DB_URL=postgresql://user:password@localhost/dbname

### 4. Initialise PostgreSQL Database
Ensure you have a PostgreSQL database running. Update the connection string in database_integration.py if necessary.

### 5. Run the Application
Start the FastAPI server:
uvicorn app:app --host 0.0.0.0 --port 8000

## How It Works
### 1. Resume Parsing
When a resume is uploaded:

The system detects whether the resume is single-column or multi-column.
An AI Agent parses the text into structured JSON (name, skills, education, experience).
An embedding is generated and added to the ChromaDB index.
### 2. Job Matching
When a job is posted:

An embedding is generated for the job description.
The system searches the ChromaDB index for similar candidate embeddings.
An embedding model evaluates the match and assigns an ATS score.






