# LLM-based-ATS
This project implements an AI-powered Applicant Tracking System (ATS) that automates resume parsing, candidate-job matching, and talent acquisition processes. The system leverages advanced natural language processing (NLP) models, embeddings, and vector databases to streamline recruitment workflows.

Key features include:

Resume Parsing : Extracts structured data (e.g., name, skills, education, experience) from resumes using state-of-the-art LLMs.
Dynamic Layout Detection : Automatically detects single-column and multi-column resumes and uses the appropriate text extraction method (pdfplumber or PyMuPDF).
Candidate-Job Matching : Evaluates how well candidates match job descriptions using embeddings and similarity search.
FAISS Indexing : Stores and retrieves candidate embeddings efficiently using Facebook's FAISS library with PostgreSQL persistence.
Scalability : Designed to handle large datasets and complex PDF layouts.

