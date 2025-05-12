"""
Bu modul resume-ləri təhlil etmək üçün funksiyalar təmin edir.
"""

import re
import textstat

CERTIFICATION_PATTERN = r"(?i)(certification|certificate|certified|training|aws|azure|pmp|csm|sertifikat|sertifikatlar|sertifikasiya|təlim|kurs)"
EDUCATION_PATTERN = r"(?i)(education|degree|bachelor|master|phd|PhD|school|university|college|təhsil|bakalavr|magistr|doktorantura|məktəb|universitet|kollec)"
EXPERIENCE_PATTERN = r"(?i)(experience|professional\s+experience|work\s+history|employment|təcrübə|iş\s+təcrübəsi|əmək\s+fəaliyyəti|iş\s+tarixi)"


def analyze_resume(resume_text):
    """
    Resume-ni təhlil edir və rəy və keyfiyyət balı hesablayır.

    Args:
        resume_text (str): Analiz ediləcək resume mətni.

    Returns:
        dict: Rəylər və keyfiyyət balı.
    """
    feedback = []
    quality_score = 100 # Başlanğıc bal 100
    
    # Sertifikatlar üçün yoxlama
    certifications = re.findall(CERTIFICATION_PATTERN, resume_text)
    if not certifications:
        feedback.append("Sertifikatlar əlavə edilməyib")
        quality_score -= 17
    #Tehsil
    education = re.findall(EDUCATION_PATTERN, resume_text)
    if not education:
        feedback.append("Təhsil məlumatı natamamdır")
        quality_score -= 22
    #Tecrube
    experience = re.findall(EXPERIENCE_PATTERN, resume_text)
    if not experience:
        feedback.append("İş təcrübəsi kifayət qədər deyil")
        quality_score -= 25
    
    # Oxunaqlılıq indeksi üçün yoxlama
    try:
        flesch_reading_ease = textstat.flesch_reading_ease(resume_text)
        if flesch_reading_ease < 60: 
            feedback.append("CV oxunuşunu yaxşılaşdırmaq olar")
            quality_score -= 11
    except Exception as e:
        print(f"Error calculating readability score: {e}")
    
    quality_score = max(0, quality_score)
    
    return {
        "feedback": feedback,
        "quality_score": quality_score
    }


