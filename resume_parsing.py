import io
import os
import tempfile
from embedding_utils import generate_embedding
from chroma_utils import add_to_resume_chroma
from llama_cloud_services import LlamaExtract
from pydantic import BaseModel, Field

os.environ["LLAMA_CLOUD_API_KEY"] = ""

class ResumeSchema(BaseModel):
    experience: str = Field(description="Professional work experience")
    education: str = Field(description="Educational background")
    skills: list[str] = Field(description="Technical and soft skills")

llama_extract = LlamaExtract()
#agent = llama_extract.create_agent(name="resume_parser", data_schema=ResumeSchema)
agent = llama_extract.get_agent(name="resume_parser")


def parse_resume_with_llm(resume_content, name, location, file_type):
    
    try:
        if file_type not in ["pdf", "docx"]:
            raise ValueError("Unsupported file type. Only PDF and DOCX files are allowed.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            temp_file.write(resume_content)
            temp_file_path = temp_file.name 

        try:
            extracted_run = agent.extract(temp_file_path)
            extracted_data = extracted_run.data  # Access the 'data' attribute
        except Exception as e:
            raise RuntimeError(f"LlamaExtract failed: {str(e)}")

        finally:
            os.remove(temp_file_path)

        if not extracted_data:
            raise ValueError("No data extracted from the resume.")


        experience = extracted_data.get("experience", "")
        education = extracted_data.get("education", "")
        skills = extracted_data.get("skills", [])

        combined_text_for_embedding = (
            f"Experience: {experience} "
            f"Education: {education} "
            f"Skills: {skills}"
        )

        embedding = generate_embedding(combined_text_for_embedding)

        metadata = {
            "name": name,
            "location": location,
            "experience": experience,
            "education": education,
            "skills": skills,
        }

        unique_id = add_to_resume_chroma(embedding, metadata)
        
        return {"message": "Resume parsed successfully", "unique_id": unique_id}, embedding
    except Exception as e:
        return {"error": f"Failed to parse resume: {str(e)}"}, None
    




