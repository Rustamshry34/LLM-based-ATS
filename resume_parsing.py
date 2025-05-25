import io
from embedding_utils import generate_embedding
from chroma_utils import add_to_resume_chroma
from docx import Document 
from unstructured.partition.pdf import partition_pdf

def extract_text_from_pdf(file_content):

    try:
        file_like_object = io.BytesIO(file_content)
        elements = partition_pdf(file=file_like_object, strategy="auto")
        full_text = "\n".join([str(el) for el in elements])
        return full_text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_text_from_docx(file_content):
    

    try:
        file_like_object = io.BytesIO(file_content)
        doc = Document(file_like_object)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return full_text.strip()
    except Exception as e:
        print(f"Error extracting text with python-docx: {e}")
        return ""

def parse_resume_with_llm(resume_content, name, location, file_type):
    
    try:
        if file_type == "pdf":
            resume_text = extract_text_from_pdf(resume_content)
        elif file_type == "docx":
            resume_text = extract_text_from_docx(resume_content)
        else:
            raise ValueError("Unsupported file type. Only PDF and DOCX files are allowed.")

        if not resume_text or resume_text.strip() == "":
            raise ValueError("Resume text is empty after extraction.")
        
        embedding = generate_embedding(resume_text)
        
        metadata = {
            "name": name,
            "location": location,
        }

        unique_id = add_to_resume_chroma(embedding, metadata)
        
        return {"message": "Resume parsed successfully", "unique_id": unique_id}, embedding
    except Exception as e:
        return {"error": f"Failed to parse resume: {str(e)}"}, None
    




