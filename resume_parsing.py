# resume_parsing.py
import requests
import json
import re
import io
from embedding_utils import generate_embedding
from faiss_utils import add_to_faiss
import fitz  # PyMuPDF
import pdfplumber

API_KEY = ""
API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
headers = {"Authorization": f"Bearer {API_KEY}"}

def detect_pdf_layout(file_content):
    """
    Detect whether a PDF is single-column or multi-column by analyzing text block positions.
    Returns "single" for single-column and "multi" for multi-column.
    """
    try:
        file_like_object = io.BytesIO(file_content)
        
        doc = fitz.open(stream=file_like_object, filetype="pdf")
        x_positions = set()  # To store unique x0 values of text blocks
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")  
            
            for block in blocks:
                if block[6] == 0:  # Block type 0 indicates text
                    x_positions.add(round(block[0], 1)) 
        
        if len(x_positions) > 1:
            return "multi"
        else:
            return "single"
    except Exception as e:
        print(f"Error detecting PDF layout: {e}")
        return "single"  # Default to single-column if detection fails

def extract_text_with_pdfplumber(file_content):
    try:
        file_like_object = io.BytesIO(file_content)
        text = ""
        with pdfplumber.open(file_like_object) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        return ""

def extract_text_with_pymupdf(file_content):
    try:
        file_like_object = io.BytesIO(file_content)
        doc = fitz.open(stream=file_like_object, filetype="pdf")
        full_text = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")
            
            blocks.sort(key=lambda block: (block[1], block[0]))  
            
            for block in blocks:
                if block[6] == 0:  
                    text = block[4].strip()
                    if text:
                        full_text.append(text)
        
        return "\n".join(full_text).strip()
    except Exception as e:
        print(f"Error extracting text with PyMuPDF: {e}")
        return ""

def extract_text_from_pdf(file_content):
    
    layout = detect_pdf_layout(file_content)
    if layout == "single":
        return extract_text_with_pdfplumber(file_content)
    elif layout == "multi":
        return extract_text_with_pymupdf(file_content)
    else:
        return ""

def parse_resume_with_llm(resume_content):
    try:
        resume_text = extract_text_from_pdf(resume_content)
        
        if not resume_text or resume_text.strip() == "":
            raise ValueError("Resume text is empty after extraction.")
        
        prompt = f"""
        ### Instruction:
        You are a resume parser. Extract the following information from the resume below and return ONLY a valid JSON object.

        ### Resume Content:
        {resume_text}

        ### Output Format:
        {{
        "name": "Candidate's Full Name",
        "skills": ["Skill1", "Skill2", ...], 
        "education": ["Degree1 from Institution1 (Year)", "Degree2 from Institution2 (Year)", ...],
        "experience": ["JobTitle1 at Company1 (Duration)", "JobTitle2 at Company2 (Duration)", ...]
        }}

        ### Response:
        """
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "return_full_text": False  
                }
            }
        )
        result = response.json()
        print(f"The result text: {result}")

        try:
            generated_text = result[0]["generated_text"]
            
            json_match = re.search(r"```json\s*({.*?})\s*```", generated_text, re.DOTALL)
            
            if not json_match:
                json_match = re.search(r"</think>\s*(\{.*?\})", generated_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1).strip()
                parsed_data = json.loads(json_str)
            else:
                parsed_data = {"error": "Failed to parse JSON"}
        except (KeyError, json.JSONDecodeError):
            parsed_data = {"error": "Failed to parse JSON"}
        
        embedding = generate_embedding(resume_text)
        
        add_to_faiss(embedding)
        
        return parsed_data, embedding
    except Exception:
        return {"error": "Failed to parse resume"}, None
