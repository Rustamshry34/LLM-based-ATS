# faiss_utils.py
import faiss
import numpy as np
from database_integration import load_faiss_index_from_db, save_faiss_index_to_db

dimension = 768

index = load_faiss_index_from_db()
if index is None:
    index = faiss.IndexFlatL2(dimension)

def add_to_faiss(embedding):
    index.add(np.array([embedding], dtype='float32'))

def search_faiss(query_embedding, k=10):
    distances, indices = index.search(np.array([query_embedding], dtype='float32'), k)
    return indices[0]  # Return the indices of the top-k matches

def save_faiss_index():
    save_faiss_index_to_db(index)

def load_faiss_index():
    global index
    loaded_index = load_faiss_index_from_db()
    if loaded_index:
        index = loaded_index
    else:
        index = faiss.IndexFlatL2(dimension)
