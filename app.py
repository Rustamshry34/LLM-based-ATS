# app.py
import uvicorn
from api import app
from faiss_utils import load_faiss_index

load_faiss_index()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


    
    