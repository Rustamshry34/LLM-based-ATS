"""
Bu modul PostgreSQL verilənlər bazası ilə işləmək üçün funksiyalar təmin edir.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Candidate(Base):
    """
    PostgreSQL-də namizədlər üçün cədvəl təyin edir.
    """
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True)  
    name = Column(String)  
    location = Column(String) 
    feedback = Column(String)  
    quality_score = Column(Float) 

class Job(Base):
    """
    PostgreSQL-də işlər üçün cədvəl təyin edir.
    """
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True) 
    title = Column(String)
    description = Column(String)

engine = create_engine("postgresql://postgres:password@localhost:5432/Db_Name")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_candidate(parsed_data, unique_id):
    
    """
    Namizədin məlumatlarını (ad, yer, rəy və keyfiyyət balı) PostgreSQL-ə yadda saxlayır.

    Args:
        parsed_data (dict): Namizədin məlumatları.
        unique_id (str): Namizədin unikal ID-si.
    """

    feedback_list = parsed_data.get("feedback", [])
    if not isinstance(feedback_list, list):
        feedback_list = [str(feedback_list)] 

    candidate = Candidate(
        unique_id=unique_id,
        name=parsed_data.get("name"),
        location=parsed_data.get("location"),
        feedback=", ".join(feedback_list), 
        quality_score=parsed_data.get("quality_score")
    )
    session.add(candidate)
    session.commit()

def save_job(job_title, job_description, unique_id):
   
    """
    İşin məlumatlarını (ad, təsvir və unikal ID) PostgreSQL-ə yadda saxlayır.

    Args:
        job_title (str): İşin adı.
        job_description (str): İşin təsviri.
        unique_id (str): İşin unikal ID-si.
    """

    job = Job(
        unique_id=unique_id,
        title=job_title,
        description=job_description
    )
    session.add(job)
    session.commit()

def delete_candidate(unique_id):
    
    """
    PostgreSQL-dən unikal ID-yə görə namizədin məlumatlarını silir.

    Args:
        unique_id (str): Silinəcək namizədin unikal ID-si.

    Returns:
        bool: Silmə uğurlu olduqda True, əks halda False.
    """

    candidate = session.query(Candidate).filter_by(unique_id=unique_id).first()
    if candidate:
        session.delete(candidate)
        session.commit()
        return True
    return False

def delete_job(unique_id):
    
    """
    PostgreSQL-dən unikal ID-yə görə işin məlumatlarını silir.

    Args:
        unique_id (str): Silinəcək işin unikal ID-si.

    Returns:
        bool: Silmə uğurlu olduqda True, əks halda False.
    """
    job = session.query(Job).filter_by(unique_id=unique_id).first()
    if job:
        session.delete(job)
        session.commit()
        return True
    return False
    