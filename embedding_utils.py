# embedding_utils.py
from sentence_transformers import SentenceTransformer

# Load a pre-trained embedding model
#model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer("sentence-transformers/LaBSE")


def generate_embedding(text):
    """Generate an embedding for the given text."""
    if not text or not isinstance(text, str) or text.strip() == "":
        raise ValueError("Input text is empty or invalid.")
    return model.encode(text)


    