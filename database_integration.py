from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Candidate(Base):
    
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True)  
    name = Column(String)  
    location = Column(String) 

class Job(Base):
    
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True) 
    title = Column(String)
    description = Column(String)

engine = create_engine("postgresql://postgres:4559133@localhost:5432/ats_system")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_candidate(parsed_data, unique_id):

    candidate = Candidate(
        unique_id=unique_id,
        name=parsed_data.get("name"),
        location=parsed_data.get("location"),
    )
    session.add(candidate)
    session.commit()

def save_job(job_title, job_description, unique_id):

    job = Job(
        unique_id=unique_id,
        title=job_title,
        description=job_description
    )
    session.add(job)
    session.commit()

def delete_candidate(unique_id):

    candidate = session.query(Candidate).filter_by(unique_id=unique_id).first()
    if candidate:
        session.delete(candidate)
        session.commit()
        return True
    return False

def delete_job(unique_id):
    
    job = session.query(Job).filter_by(unique_id=unique_id).first()
    if job:
        session.delete(job)
        session.commit()
        return True
    return False
    