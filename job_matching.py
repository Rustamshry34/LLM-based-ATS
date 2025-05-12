"""
Bu modul işləri namizədlərə uyğunlaşdırmaq üçün funksiyalar təmin edir.
"""

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from chroma_utils import search_resume_chroma

def calculate_ats_score(job_embedding):
    """
    İşləri namizədlərə uyğunlaşdırmaq üçün ATS balı hesablayır.

    Args:
        job_embedding (list): İş üçün embedding.

    Returns:
        list: Uyğun namizədlərin siyahısı.
    """
    try:
        # Resume kolleksiyasında axtarış edin

        search_results = search_resume_chroma(job_embedding, k=10)
        candidate_ids = search_results['ids'][0]
        candidate_embeddings = search_results['embeddings'][0]
        candidate_metadatas = search_results['metadatas'][0]
        
        matched_candidates = []
        for i, candidate_id in enumerate(candidate_ids):
            # Namizəd meta-məlumatlarını və embedding-lərini alın

            candidate_metadata = candidate_metadatas[i]
            candidate_embedding = np.array(candidate_embeddings[i])
            
            # İş və namizəd embedding-ləri arasındakı oxşarlığı hesablayın
            similarity_score = cosine_similarity([job_embedding], [candidate_embedding])[0][0]
            
            # Meta-məlumatları yalnız ad və yerləşdiyi yerə endirin
            filtered_metadata = {
                "name": candidate_metadata.get("name"),
                "location": candidate_metadata.get("location")
            }
            
            # Namizədi oxşarlıq balı ilə əlavə edin
            matched_candidates.append({
                "candidate_id": candidate_id,
                "score": similarity_score,
                "metadata": filtered_metadata
            })
            
        # Namizədləri oxşarlıq balına görə sıralayın
        matched_candidates.sort(key=lambda x: x["score"], reverse=True)
        return matched_candidates
    except Exception:
        raise


    

