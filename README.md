
# AI-Powered Applicant Tracking System (ATS)

[![Deploy ATS to AWS](https://github.com/Rustamshry34/LLM-based-ATS/actions/workflows/deploy.yml/badge.svg)](https://github.com/Rustamshry34/LLM-based-ATS/actions/workflows/deploy.yml)

An intelligent, cloud-native ATS that leverages LLMs and semantic search to automate resume parsing, candidate-job matching, and talent management.

## 🌟 Features
 - AI-Powered Resume Parsing: Extract structured data from PDF/DOCX resumes using Llama Cloud
 - Semantic Matching: Match candidates to jobs using cosine similarity on embeddings
 - Persistent Storage: ChromaDB for vector storage + PostgreSQL for relational data
 - Production-Ready: Fully containerized with Docker, deployed via Terraform on AWS
 - Secure & Scalable: Infrastructure-as-Code with remote state management

## 🧠 Core Components
### 1. Resume Parsing
 - Uses Llama Cloud with a custom agent (resume_parser) to extract:
 - Professional experience
 - Educational background
 - Technical & soft skills
 - Supports PDF and DOCX formats (max 5 MB)
 - Sanitizes inputs and validates file types

### 2. Embedding Generation
 - Generates dense vector representations using sentence-transformers/all-MiniLM-L6-v2
 - Combines experience, education, and skills into a single embedding
 - CPU-optimized (no GPU required)

### 3. Candidate-Job Matching
 - Computes cosine similarity between job and candidate embeddings
 - Returns top-k matches with scores (0.0–1.0)
 - Real-time matching against all posted jobs

### 4. Database Integration
- ChromaDB: Stores embeddings and metadata with persistent EBS volume
- PostgreSQL (RDS): Relational storage for candidates and jobs
- Dual-write architecture ensures data consistency
- Secure connection via environment variables

### 5. RESTful API (FastAPI)
 - /upload-resume/ — Parse and store resumes
 - /post-job/ — Create job postings
 - /match-candidates/ — Get ranked candidate matches
 - /delete-resume/, /delete-job/ — Data management
 - Built-in validation, error handling, and Sentry integration

### 6. Cloud Deployment (AWS)
Infrastructure: Terraform-managed
 - EC2 (t3.micro) for app
 - RDS (db.t4g.micro) for PostgreSQL
 - EBS volume for ChromaDB persistence
 - S3 + DynamoDB for Terraform remote state

CI/CD: GitHub Actions
 - Builds Docker image → pushes to GHCR
 - Applies Terraform config
 - Deploys container to EC2

Security:
 - SSH key rotation per deploy
 - Secrets via GitHub Secrets
 - Minimal IAM permissions
