"""
Bu modul Chroma DB ilə işləmək üçün funksiyalar təmin edir.
"""

import chromadb
from chromadb.utils import embedding_functions
import os
import uuid

# Daimi saxlamaq üçün direktoriya təyin edin
PERSIST_DIRECTORY = "./chroma_db_data"

# Direktorinin mövcud olduğundan əmin olun
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# Chroma DB müştərisini daimi saxlamaqla işə salmaq
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

# MiniLM-dən istifadə edərək embedding funksiyasını təyin etmek
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Resume kolleksiyasını yaradın və ya yükləyin
resume_collection = client.get_or_create_collection(name="resume_collection", embedding_function=embedding_fn)

# İş kolleksiyasını yaradın və ya yükləyin
job_collection = client.get_or_create_collection(name="job_collection", embedding_function=embedding_fn)


def add_to_resume_chroma(embedding, metadata):

    """
    Resume kolleksiyasına embedding əlavə edir.

    Args:
        embedding (list): Yeni resume üçün embedding.
        metadata (dict): Resume ilə bağlı meta-məlumatlar.

    Returns:
        str: Yaradılmış unikal ID.
    """

    unique_id = str(uuid.uuid4())
    resume_collection.add(ids=[unique_id], embeddings=[embedding], metadatas=[metadata])
    return unique_id  

def add_to_job_chroma(embedding, metadata):

    """
    İş kolleksiyasına embedding əlavə edir.

    Args:
        embedding (list): Yeni iş üçün embedding.
        metadata (dict): İş ilə bağlı meta-məlumatlar.

    Returns:
        str: Yaradılmış unikal ID.
    """

    unique_id = str(uuid.uuid4())
    job_collection.add(ids=[unique_id], embeddings=[embedding], metadatas=[metadata])
    return unique_id

def search_resume_chroma(query_embedding, k=10):

    """
    Resume kolleksiyasında oxşar embedding-ləri axtarır.

    Args:
        query_embedding (list): Axtarış üçün sorğu embedding-i.
        k (int): Qaytarılacaq nəticələrin sayı.

    Returns:
        dict: Axtarış nəticələri.
    """

    results = resume_collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["embeddings", "metadatas"] 
    )
    return results

def search_job_chroma(query_embedding, k=10):

    """
    İş kolleksiyasında oxşar embedding-ləri axtarır.

    Args:
        query_embedding (list): Axtarış üçün sorğu embedding-i.
        k (int): Qaytarılacaq nəticələrin sayı.

    Returns:
        dict: Axtarış nəticələri.
    """

    results = job_collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["embeddings", "metadatas"]  
    )
    return results

def get_all_resumes_from_chroma():
    
    """
    Chroma DB-dən bütün resume-lərin embedding-lərini və meta-məlumatlarını alır.

    Returns:
        tuple: Resume ID-ləri, embedding-lər və meta-məlumatlar.
    """

    results = resume_collection.get(include=["embeddings", "metadatas"])
    return results['ids'], results['embeddings'], results['metadatas']

def get_all_jobs_from_chroma():

    """
    Chroma DB-dən bütün işlərin embedding-lərini və meta-məlumatlarını alır.

    Returns:
        tuple: İş ID-ləri, embedding-lər və meta-məlumatlar.
    """
  
    results = job_collection.get(include=["embeddings", "metadatas"])
    return results['ids'], results['embeddings'], results['metadatas']

def delete_resume_from_chroma(unique_id):

    """
    Resume kolleksiyasından unikal ID-yə görə resume silir.

    Args:
        unique_id (str): Silinəcək resume-in unikal ID-si.
    """

    resume_collection.delete(ids=[unique_id])

def delete_job_from_chroma(unique_id):

    """
    İş kolleksiyasından unikal ID-yə görə iş silir.

    Args:
        unique_id (str): Silinəcək işin unikal ID-si.
    """

    job_collection.delete(ids=[unique_id])    


    