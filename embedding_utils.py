import os
os.environ["SENTENCE_TRANSFORMERS_DISABLE_ONNX"] = "1"


from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def generate_embedding(text):

    if not text or not isinstance(text, str) or text.strip() == "":
        raise ValueError("Input text is empty or invalid.")
    return model.encode(text)

    