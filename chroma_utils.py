import chromadb
from chromadb.utils import embedding_functions
import os
import uuid

PERSIST_DIRECTORY = "./chroma_db_data"

os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

resume_collection = client.get_or_create_collection(name="resume_collection", embedding_function=embedding_fn)

job_collection = client.get_or_create_collection(name="job_collection", embedding_function=embedding_fn)


def add_to_resume_chroma(embedding, metadata):

    unique_id = str(uuid.uuid4())
    resume_collection.add(ids=[unique_id], embeddings=[embedding], metadatas=[metadata])
    return unique_id  

def add_to_job_chroma(embedding, metadata):

    unique_id = str(uuid.uuid4())
    job_collection.add(ids=[unique_id], embeddings=[embedding], metadatas=[metadata])
    return unique_id

def search_resume_chroma(query_embedding, k=10):

    results = resume_collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["embeddings", "metadatas"] 
    )
    return results

def search_job_chroma(query_embedding, k=10):

    results = job_collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["embeddings", "metadatas"]  
    )
    return results

def get_all_jobs_from_chroma():
  
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


    