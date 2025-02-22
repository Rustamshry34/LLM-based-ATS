# database_integration.py
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import faiss
import numpy as np

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    resume_text = Column(LargeBinary)  # Store raw binary content
    skills = Column(Text)
    education = Column(Text)
    experience = Column(Text)
    embedding = Column(LargeBinary)  # Store the embedding as binary data

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    embedding = Column(LargeBinary)  # Store the embedding as binary data

class FaissIndex(Base):
    __tablename__ = 'faiss_index'
    id = Column(Integer, primary_key=True)
    index_data = Column(LargeBinary)  # Store the serialized FAISS index

# Initialize database
engine = create_engine('postgresql://postgres:liberal455@localhost:5432/ats_system')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_candidate(name, resume_content, parsed_data, embedding):
    if embedding is None:
        raise ValueError("Embedding cannot be None.")
    
    candidate = Candidate(
        name=name,
        resume_text=resume_content,  # Store raw binary content
        skills=" ".join(parsed_data.get("skills", [])),
        education=" ".join(parsed_data.get("education", [])),
        experience=" ".join(parsed_data.get("experience", [])),
        embedding=embedding.tobytes()  # Convert embedding to binary
    )
    session.add(candidate)
    session.commit()

def save_job(title, description, embedding):
    if embedding is None:
        raise ValueError("Embedding cannot be None.")
    
    job = Job(title=title, description=description, embedding=embedding.tobytes())
    session.add(job)
    session.commit()

def load_embedding_from_db(embedding_bytes):
    """Convert binary embedding data back to a NumPy array."""
    return np.frombuffer(embedding_bytes, dtype='float32')

def save_faiss_index_to_db(index):
    """Save the serialized FAISS index to PostgreSQL."""
    try:
        serialized_index = faiss.serialize_index(index)  # Serialize the FAISS index
        db_index = session.query(FaissIndex).first()
        if db_index:
            db_index.index_data = serialized_index
        else:
            db_index = FaissIndex(index_data=serialized_index)
            session.add(db_index)
        session.commit()
    except Exception as e:
        print(f"Error saving FAISS index to database: {e}")

def load_faiss_index_from_db():
    """Load the FAISS index from PostgreSQL."""
    db_index = session.query(FaissIndex).first()
    if db_index and db_index.index_data:
        try:
            return faiss.deserialize_index(db_index.index_data)  # Deserialize the FAISS index
        except Exception as e:
            print(f"Error deserializing FAISS index: {e}. Initializing a new index.")
            return None
    return None

