import pandas as pd
import numpy as np
from datetime import datetime

# Treatment and medication recommendations database
TREATMENT_RECOMMENDATIONS = {
    'Flu': {
        'medications': [
            {'name': 'Oseltamivir (Tamiflu)', 'dosage': '75mg twice daily', 'duration': '5 days', 'type': 'antiviral'},
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'symptom relief'},
            {'name': 'Ibuprofen', 'dosage': '400mg every 6-8 hours', 'duration': 'as needed', 'type': 'anti-inflammatory'}
        ],
        'treatments': [
            'Rest and adequate sleep (8-10 hours)',
            'Increase fluid intake (8-10 glasses water daily)',
            'Use humidifier or steam inhalation',
            'Warm salt water gargling for sore throat',
            'Avoid contact with others for 24 hours after fever breaks'
        ],
        'warnings': [
            'Seek immediate care if difficulty breathing',
            'Monitor for high fever (>103°F) persisting >3 days',
            'Watch for signs of dehydration'
        ]
    },
    'COVID-19': {
        'medications': [
            {'name': 'Paxlovid (if eligible)', 'dosage': 'As prescribed', 'duration': '5 days', 'type': 'antiviral'},
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'symptom relief'},
            {'name': 'Dextromethorphan', 'dosage': '15-30mg every 4 hours', 'duration': 'as needed', 'type': 'cough suppressant'}
        ],
        'treatments': [
            'Isolate for at least 5 days from symptom onset',
            'Rest and adequate sleep',
            'Monitor oxygen saturation if available',
            'Increase fluid intake',
            'Prone positioning if breathing difficulties'
        ],
        'warnings': [
            'URGENT: Seek immediate care for difficulty breathing',
            'Monitor for persistent chest pain',
            'Watch for confusion or inability to stay awake',
            'Check oxygen levels if pulse oximeter available'
        ]
    },
    'Common Cold': {
        'medications': [
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'symptom relief'},
            {'name': 'Pseudoephedrine', 'dosage': '60mg every 6 hours', 'duration': '3-5 days', 'type': 'decongestant'},
            {'name': 'Zinc lozenges', 'dosage': '1 lozenge every 2 hours', 'duration': '7 days', 'type': 'immune support'}
        ],
        'treatments': [
            'Rest and adequate sleep',
            'Increase fluid intake, especially warm liquids',
            'Use saline nasal spray or rinse',
            'Honey for cough relief (not for children under 1 year)',
            'Warm compress for sinus pressure'
        ],
        'warnings': [
            'See doctor if symptoms worsen after 7 days',
            'Watch for high fever (>101.5°F)',
            'Monitor for severe headache or sinus pain'
        ]
    },
    'Pneumonia': {
        'medications': [
            {'name': 'Amoxicillin', 'dosage': '500mg every 8 hours', 'duration': '7-10 days', 'type': 'antibiotic'},
            {'name': 'Azithromycin', 'dosage': '500mg day 1, then 250mg daily', 'duration': '5 days', 'type': 'antibiotic'},
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'symptom relief'}
        ],
        'treatments': [
            'Complete prescribed antibiotic course',
            'Rest and avoid strenuous activity',
            'Increase fluid intake significantly',
            'Use humidifier or steam inhalation',
            'Monitor temperature regularly'
        ],
        'warnings': [
            'URGENT: Seek immediate care for severe breathing difficulty',
            'Monitor for chest pain or rapid breathing',
            'Watch for persistent high fever',
            'This condition requires medical supervision'
        ]
    },
    'Bronchitis': {
        'medications': [
            {'name': 'Guaifenesin', 'dosage': '400mg every 4 hours', 'duration': '7-10 days', 'type': 'expectorant'},
            {'name': 'Dextromethorphan', 'dosage': '15-30mg every 4 hours', 'duration': 'as needed', 'type': 'cough suppressant'},
            {'name': 'Ibuprofen', 'dosage': '400mg every 6-8 hours', 'duration': 'as needed', 'type': 'anti-inflammatory'}
        ],
        'treatments': [
            'Rest and avoid smoking/irritants',
            'Use humidifier or steam inhalation',
            'Drink warm liquids (tea, broth)',
            'Honey for cough relief',
            'Avoid cough suppressants if producing mucus'
        ],
        'warnings': [
            'See doctor if cough persists >3 weeks',
            'Watch for blood in sputum',
            'Monitor for high fever or difficulty breathing'
        ]
    },
    'Asthma': {
        'medications': [
            {'name': 'Albuterol inhaler', 'dosage': '2 puffs every 4-6 hours', 'duration': 'as needed', 'type': 'bronchodilator'},
            {'name': 'Budesonide inhaler', 'dosage': '2 puffs twice daily', 'duration': 'long-term control', 'type': 'corticosteroid'},
            {'name': 'Prednisone', 'dosage': '40-60mg daily', 'duration': '5-7 days', 'type': 'oral steroid (severe cases)'}
        ],
        'treatments': [
            'Identify and avoid triggers',
            'Use peak flow meter to monitor breathing',
            'Keep rescue inhaler always available',
            'Follow asthma action plan',
            'Regular follow-up with pulmonologist'
        ],
        'warnings': [
            'EMERGENCY: Call 911 for severe breathing difficulty',
            'Use rescue inhaler and seek immediate care if not improving',
            'Monitor peak flow readings',
            'This condition requires ongoing medical management'
        ]
    },
    'Headache': {
        'medications': [
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'analgesic'},
            {'name': 'Ibuprofen', 'dosage': '400mg every 6-8 hours', 'duration': 'as needed', 'type': 'anti-inflammatory'},
            {'name': 'Aspirin', 'dosage': '325-650mg every 4 hours', 'duration': 'as needed', 'type': 'analgesic'}
        ],
        'treatments': [
            'Rest in quiet, dark room',
            'Apply cold or warm compress to head/neck',
            'Stay hydrated',
            'Practice relaxation techniques',
            'Maintain regular sleep schedule'
        ],
        'warnings': [
            'URGENT: Sudden severe headache unlike any before',
            'Headache with fever, stiff neck, or rash',
            'Headache with vision changes or weakness',
            'See doctor for frequent or worsening headaches'
        ]
    },
    'Migraine': {
        'medications': [
            {'name': 'Sumatriptan', 'dosage': '50-100mg at onset', 'duration': 'single dose', 'type': 'triptan'},
            {'name': 'Acetaminophen + Caffeine', 'dosage': '2 tablets at onset', 'duration': 'single dose', 'type': 'combination analgesic'},
            {'name': 'Topiramate', 'dosage': '25-100mg daily', 'duration': 'preventive', 'type': 'anticonvulsant'}
        ],
        'treatments': [
            'Rest in quiet, dark room immediately',
            'Apply cold compress to forehead',
            'Stay hydrated but avoid triggers',
            'Practice stress management',
            'Maintain consistent sleep schedule'
        ],
        'warnings': [
            'Track triggers and patterns',
            'See neurologist for frequent migraines',
            'Watch for changes in migraine pattern',
            'Avoid overuse of pain medications'
        ]
    },
    'Tonsillitis': {
        'medications': [
            {'name': 'Amoxicillin', 'dosage': '500mg every 8 hours', 'duration': '10 days', 'type': 'antibiotic'},
            {'name': 'Acetaminophen', 'dosage': '650mg every 6 hours', 'duration': 'as needed', 'type': 'analgesic'},
            {'name': 'Ibuprofen', 'dosage': '400mg every 6-8 hours', 'duration': 'as needed', 'type': 'anti-inflammatory'}
        ],
        'treatments': [
            'Warm salt water gargling 3-4 times daily',
            'Increase fluid intake, prefer cool liquids',
            'Rest and avoid irritants',
            'Use throat lozenges for comfort',
            'Complete full course of antibiotics if prescribed'
        ],
        'warnings': [
            'See doctor for severe throat pain with difficulty swallowing',
            'Watch for breathing difficulties',
            'Monitor for high fever or enlarged lymph nodes',
            'Complete antibiotic course to prevent complications'
        ]
    }
}

def get_personalized_recommendations(diagnosis, patient_data=None):
    """
    Get personalized treatment recommendations based on diagnosis and patient data
    """
    base_recommendations = TREATMENT_RECOMMENDATIONS.get(diagnosis, {
        'medications': [],
        'treatments': ['Consult with healthcare provider for appropriate treatment'],
        'warnings': ['This condition requires professional medical evaluation']
    })
    
    # Personalize based on patient data if available
    if patient_data:
        recommendations = personalize_treatment(base_recommendations, patient_data)
    else:
        recommendations = base_recommendations
    
    # Add standard medical disclaimer
    recommendations['disclaimer'] = get_medical_disclaimer()
    
    return recommendations

def personalize_treatment(base_recommendations, patient_data):
    """
    Personalize treatment recommendations based on patient history and data
    """
    personalized = base_recommendations.copy()
    
    # Age-based modifications
    age = patient_data.get('age', 0)
    if age < 18:
        personalized['pediatric_note'] = "Dosages may need adjustment for pediatric patients. Consult pediatrician."
    elif age > 65:
        personalized['geriatric_note'] = "Consider reduced dosages and monitor for drug interactions in elderly patients."
    
    # Allergy considerations
    allergies = patient_data.get('allergies', [])
    if allergies:
        personalized['allergy_warnings'] = f"Patient allergies noted: {', '.join(allergies)}. Avoid contraindicated medications."
    
    # Chronic conditions considerations
    chronic_conditions = patient_data.get('chronic_conditions', [])
    if chronic_conditions:
        condition_warnings = []
        
        if 'diabetes' in chronic_conditions:
            condition_warnings.append("Monitor blood sugar levels; some medications may affect glucose.")
        
        if 'hypertension' in chronic_conditions:
            condition_warnings.append("Monitor blood pressure; avoid medications that may increase BP.")
        
        if 'kidney_disease' in chronic_conditions:
            condition_warnings.append("Adjust dosages for renal function; avoid nephrotoxic medications.")
        
        if 'liver_disease' in chronic_conditions:
            condition_warnings.append("Consider hepatic metabolism; avoid hepatotoxic medications.")
        
        if condition_warnings:
            personalized['chronic_condition_warnings'] = condition_warnings
    
    # Current medications (drug interactions)
    current_medications = patient_data.get('current_medications', [])
    if current_medications:
        personalized['interaction_warning'] = f"Review for drug interactions with current medications: {', '.join(current_medications)}"
    
    return personalized

def get_medical_disclaimer():
    """
    Get the standard medical disclaimer
    """
    return {
        'important_notice': [
            "🚨 MEDICAL DISCLAIMER: This AI system is a decision-support tool only and NOT a replacement for professional medical advice.",
            "👨‍⚕️ FINAL DECISIONS must be confirmed by a licensed healthcare provider.",
            "🏥 For emergency symptoms, seek immediate medical attention or call emergency services.",
            "💊 Do not start, stop, or change medications without consulting your doctor.",
            "📋 This recommendation is based on symptoms only and may not account for all medical factors.",
            "⚖️ Healthcare providers should use their clinical judgment and consider complete patient history."
        ],
        'emergency_signs': [
            "Difficulty breathing or shortness of breath",
            "Chest pain or pressure",
            "Severe or persistent vomiting",
            "High fever (>103°F/39.4°C)",
            "Signs of severe dehydration",
            "Sudden severe headache",
            "Confusion or altered mental state"
        ]
    }

def analyze_symptom_patterns(patient_history):
    """
    Analyze patterns in patient's symptom history for better predictions
    """
    if not patient_history:
        return None
    
    # Analyze frequency of symptoms
    symptom_frequency = {}
    diagnosis_history = []
    
    for record in patient_history:
        # Count symptom occurrences
        for symptom in record.get('symptoms', []):
            symptom_frequency[symptom] = symptom_frequency.get(symptom, 0) + 1
        
        # Track diagnosis history
        if 'diagnosis' in record:
            diagnosis_history.append(record['diagnosis'])
    
    return {
        'common_symptoms': symptom_frequency,
        'diagnosis_history': diagnosis_history,
        'total_visits': len(patient_history)
    }
