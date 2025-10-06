
def extract_conditions_from_text(user_input):
    """
    Extract possible conditions from user input using NLP and keyword matching
    
    Args:
        user_input (str): User's symptom description
        
    Returns:
        list: List of possible conditions with reasoning
    """
    
    user_text = user_input.lower()
    possible_conditions = []
    
    # Condition keyword patterns (generated from dataset analysis)
    condition_patterns = {
        'Common Cold': ['cold', 'runny nose', 'sneezing', 'congestion'],
        'Flu': ['flu', 'influenza', 'fever', 'body aches', 'chills'],
        'COVID-19': ['covid', 'coronavirus', 'loss of taste', 'loss of smell'],
        'Pneumonia': ['pneumonia', 'chest infection', 'productive cough'],
        'Bronchitis': ['bronchitis', 'persistent cough', 'phlegm'],
        'Asthma': ['asthma', 'wheezing', 'breathing problems'],
        'Allergies': ['allergies', 'sneezing', 'itchy eyes', 'seasonal'],
        'Sinusitis': ['sinus', 'facial pressure', 'nasal congestion'],
        'Migraine': ['migraine', 'severe headache', 'light sensitivity'],
        'Tension Headache': ['tension headache', 'pressure headache'],
        'Gastroenteritis': ['stomach bug', 'food poisoning', 'stomach flu'],
        'UTI': ['urinary', 'burning urination', 'frequent urination'],
        'Strep Throat': ['strep', 'severe sore throat', 'throat infection'],
        'Ear Infection': ['ear infection', 'ear pain', 'hearing problems'],
        'Hypertension': ['high blood pressure', 'hypertension', 'elevated bp'],
        'Diabetes': ['diabetes', 'high blood sugar', 'frequent urination'],
        'Anxiety': ['anxiety', 'panic', 'worry', 'nervousness'],
        'Depression': ['depression', 'sadness', 'low mood', 'hopelessness'],
        'Arthritis': ['arthritis', 'joint pain', 'stiffness'],
        'Back Pain': ['back pain', 'lower back', 'spine pain'],
    }
    
    # Extract conditions based on keyword matching
    for condition, keywords in condition_patterns.items():
        matches = []
        for keyword in keywords:
            if keyword in user_text:
                matches.append(keyword)
        
        if matches:
            confidence_score = len(matches) / len(keywords)  # Simple scoring
            possible_conditions.append({
                'condition': condition,
                'matched_keywords': matches,
                'reasoning': f"Detected keywords: {', '.join(matches)}",
                'match_score': confidence_score
            })
    
    # Sort by match score (most likely first)
    possible_conditions.sort(key=lambda x: x['match_score'], reverse=True)
    
    return possible_conditions[:3]  # Return top 3 matches
