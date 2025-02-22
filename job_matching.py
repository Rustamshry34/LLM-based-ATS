# job_matching.py
import requests
import re

API_KEY = ""
API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
headers = {"Authorization": f"Bearer {API_KEY}"}

def calculate_ats_score_with_llm(parsed_data, job_description):
    prompt = f"""
    ### Instruction:
    Evaluate how well the candidate matches the job description. Assign a score between 0 and 1, where 1 means a 
    perfect match and 0 means no match. Provide the score and a brief explanation.

    ### Candidate Profile:
    Skills: {parsed_data.get("skills", [])}
    Education: {parsed_data.get("education", [])}
    Work Experience: {parsed_data.get("experience", [])}

    ### Job Description:
    {job_description}

    ### Output Format:
    Score: <score between 0 and 1>
    Explanation: <brief explanation>
    """
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "parameters": {
                "return_full_text": False  # Ensure only the generated text is returned
            }
        }
    )
    result = response.json()
    
    try:
        generated_text = result[0]["generated_text"]
        
        think_match = re.search(r"</think>\s*(.*)", generated_text, re.DOTALL)
        if think_match:
            extracted_text = think_match.group(1).strip()
        else:
            extracted_text = generated_text.strip() 
        
        score_match = re.search(r"Score:\s*([0-9.]+)", extracted_text)
        score = float(score_match.group(1)) if score_match else 0.0
        
        explanation_match = re.search(r"Explanation:\s*(.+)", extracted_text, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else "Failed to parse explanation"
    except (KeyError, ValueError):
        score = 0.0
        explanation = "Failed to parse score and explanation"
    
    return {"score": score, "explanation": explanation}

