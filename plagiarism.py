import re
import math
from collections import Counter

def get_cosine_similarity(text1, text2):
    """
    Computes the cosine similarity between two text strings.
    """
    # Tokenize and clean text
    def tokenize(text):
        words = re.findall(r'\w+', text.lower())
        return words

    words1 = tokenize(text1)
    words2 = tokenize(text2)
    
    # Count frequencies
    vec1 = Counter(words1)
    vec2 = Counter(words2)
    
    # Intersection of keys
    intersection = set(vec1.keys()) & set(vec2.keys())
    
    # Dot product
    dot_product = sum(vec1[x] * vec2[x] for x in intersection)
    
    # Magnitudes
    sum1 = sum(vec1[x]**2 for x in vec1.keys())
    sum2 = sum(vec2[x]**2 for x in vec2.keys())
    
    magnitude1 = math.sqrt(sum1)
    magnitude2 = math.sqrt(sum2)
    
    if not magnitude1 or not magnitude2:
        return 0.0
    else:
        return float(dot_product) / (magnitude1 * magnitude2)

def check_plagiarism(new_text, subject_id, threshold=0.85):
    """
    Checks if new_text is similar to any existing VERIFIED content
    in the same subject.
    Returns (is_plagiarized, similarity_score, duplicate_record_id)
    """
    from app import app, StudyHistory
    with app.app_context():
        # Only compare against verified high-quality content
        existing_records = StudyHistory.query.filter_by(
            subject_id=subject_id, 
            status="verified"
        ).all()
        
        for record in existing_records:
            # Combine summary and notes for comparison
            combined_existing = (record.summary or "") + " " + (record.short_notes or "")
            score = get_cosine_similarity(new_text, combined_existing)
            
            if score >= threshold:
                return True, score, record.id
                
    return False, 0.0, None
