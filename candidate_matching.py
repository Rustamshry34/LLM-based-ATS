"""
Bu modul namizədləri işlərə uyğunlaşdırmaq üçün funksiyalar təmin edir.
"""

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from chroma_utils import search_job_chroma


def calculate_candidate_job_score(candidate_embedding):
    """
    Namizədləri işlərə uyğunlaşdırmaq üçün bal hesablayır.

    Args:
        candidate_embedding (list): Namizəd üçün embedding.

    Returns:
        list: Uyğun işlərin siyahısı.
    """
    try:
        # İş kolleksiyasında axtarış
        search_results = search_job_chroma(candidate_embedding, k=10)
        job_ids = search_results['ids'][0]
        job_embeddings = search_results['embeddings'][0]
        job_metadatas = search_results['metadatas'][0]
        
        matched_jobs = []
        for i, job_id in enumerate(job_ids):
            # İş meta-məlumatlarını və embedding-lərini alın

            job_metadata = job_metadatas[i]
            job_embedding = np.array(job_embeddings[i])

            # Namizəd və iş embedding-ləri arasındakı oxşarlığı hesablayın
            similarity_score = cosine_similarity([candidate_embedding], [job_embedding])[0][0]
            
            # İşi oxşarlıq balı ilə əlavə edin
            matched_jobs.append({
                "job_id": job_id,
                "score": similarity_score,
                "metadata": job_metadata
            })
            
        # İşləri oxşarlıq balına görə sıralayın
        matched_jobs.sort(key=lambda x: x["score"], reverse=True)
        return matched_jobs
    except Exception:
        raise 