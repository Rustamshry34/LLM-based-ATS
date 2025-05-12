"""
Bu modul resume-ləri analiz etmək və onlardan mətn çıxarmaq üçün funksiyalar təmin edir.
"""

import io
from embedding_utils import generate_embedding
from chroma_utils import add_to_resume_chroma
from resume_analysis import analyze_resume
from docx import Document 
from unstructured.partition.pdf import partition_pdf

def extract_text_from_pdf(file_content):

    try:
        file_like_object = io.BytesIO(file_content)
        elements = partition_pdf(file=file_like_object, strategy="auto")
        full_text = "\n".join([str(el) for el in elements])
        return full_text.strip()
    except Exception as e:
        print(f"PDF-dən mətn çıxarılarkən səhv: {e}")
        return ""

def extract_text_from_docx(file_content):
    
    """
    DOCX fayldan mətn çıxarır.

    Args:
        file_content (bytes): DOCX faylın içərisindəki məzmun.

    Returns:
        str: Fayldan çıxarılmış mətn.

    Raises:
        Exception: Mətn çıxarılarkən səhv baş verərsə.
    """

    try:
        file_like_object = io.BytesIO(file_content)
        doc = Document(file_like_object)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return full_text.strip()
    except Exception as e:
        print(f"Error extracting text with python-docx: {e}")
        return ""

def parse_resume_with_llm(resume_content, name, location, file_type):
    """
    Resume-ni təhlil edir və onun embedding-lərini yaradır.

    Args:
        resume_content (bytes): Resume faylının içərisindəki məzmun.
        name (str): Namizədin adı.
        location (str): Namizədin yerləşdiyi yer.
        file_type (str): Faylın növü ("pdf" və ya "docx").

    Returns:
        dict: Təhlil nəticələri və embedding.
    """
            
    # Fayl növünə görə mətn çıxarın
    try:
        if file_type == "pdf":
            resume_text = extract_text_from_pdf(resume_content)
        elif file_type == "docx":
            resume_text = extract_text_from_docx(resume_content)
        else:
            raise ValueError("Unsupported file type. Only PDF and DOCX files are allowed.")

        if not resume_text or resume_text.strip() == "":
            raise ValueError("Resume text is empty after extraction.")

        # Resume-ni təhlil edin
        analysis = analyze_resume(resume_text)
        feedback = analysis["feedback"]
        quality_score = analysis["quality_score"]
        
        # Embedding yaradın
        embedding = generate_embedding(resume_text)
        
        # Rəyləri string-ə çevirin
        feedback_string = ", ".join(feedback) if feedback else ""
        
        # Embedding-i Chroma DB-yə əlavə edin
        metadata = {
            "name": name,
            "location": location,
            "feedback": feedback_string, # Rəylər string kimi
            "quality_score": quality_score
        }

        unique_id = add_to_resume_chroma(embedding, metadata)
        
        return {"message": "Resume parsed successfully", "unique_id": unique_id, "feedback": feedback, "quality_score": quality_score }, embedding
    except Exception as e:
        return {"error": f"Failed to parse resume: {str(e)}"}, None
    




