# embedding_utils.py
from sentence_transformers import SentenceTransformer

#model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer("sentence-transformers/LaBSE")


def generate_embedding(text):
    if not text or not isinstance(text, str) or text.strip() == "":
        raise ValueError("Input text is empty or invalid.")
    return model.encode(text)


    
