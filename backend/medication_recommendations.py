#!/usr/bin/env python3
"""
Medication Recommendations System for MediChain AI
Provides medication suggestions for various diagnoses
"""

class MedicationRecommendations:
    """Comprehensive medication recommendations for various medical conditions"""
    
    def __init__(self):
        self.medication_map = {
            # Respiratory Conditions
            'Pneumonia': {
                'medications': ['Amoxicillin 500mg', 'Azithromycin 250mg', 'Ceftriaxone 1g'],
                'dosage': 'Take as prescribed by healthcare provider',
                'duration': '7-10 days',
                'instructions': 'Complete full course even if feeling better'
            },
            'Bronchitis': {
                'medications': ['Albuterol inhaler', 'Dextromethorphan', 'Guaifenesin'],
                'dosage': 'Follow package instructions',
                'duration': '5-7 days',
                'instructions': 'Use bronchodilator for breathing difficulty'
            },
            'Asthma_Attack': {
                'medications': ['Albuterol inhaler', 'Prednisone 20mg', 'Ipratropium bromide'],
                'dosage': 'Emergency: 2 puffs every 20 minutes',
                'duration': 'As needed for symptoms',
                'instructions': 'Seek immediate medical attention if severe'
            },
            'Upper_Respiratory_Infection': {
                'medications': ['Acetaminophen 500mg', 'Phenylephrine 10mg', 'Lozenges'],
                'dosage': 'Every 4-6 hours as needed',
                'duration': '7-10 days',
                'instructions': 'Rest and increase fluid intake'
            },
            'COVID_19': {
                'medications': ['Acetaminophen 500mg', 'Vitamin D', 'Zinc supplements'],
                'dosage': 'Follow healthcare provider guidance',
                'duration': '10-14 days isolation',
                'instructions': 'Monitor symptoms, seek care if worsening'
            },
            'Common_Cold': {
                'medications': ['Acetaminophen 500mg', 'Pseudoephedrine 30mg', 'Throat lozenges'],
                'dosage': 'Every 4-6 hours as needed',
                'duration': '7-10 days',
                'instructions': 'Rest, fluids, and symptomatic relief'
            },
            
            # Gastrointestinal Conditions
            'Gastroenteritis': {
                'medications': ['Loperamide 2mg', 'Oral rehydration salts', 'Probiotics'],
                'dosage': 'After each loose stool',
                'duration': '3-5 days',
                'instructions': 'Maintain hydration, BRAT diet'
            },
            'Food_Poisoning': {
                'medications': ['Oral rehydration therapy', 'Ondansetron 4mg', 'Probiotics'],
                'dosage': 'Small frequent sips',
                'duration': '24-48 hours',
                'instructions': 'Clear liquids first, avoid dairy'
            },
            'GERD': {
                'medications': ['Omeprazole 20mg', 'Ranitidine 150mg', 'Antacids'],
                'dosage': 'Once daily before breakfast',
                'duration': '4-8 weeks',
                'instructions': 'Avoid trigger foods, elevate head when sleeping'
            },
            
            # Neurological Conditions
            'Migraine': {
                'medications': ['Sumatriptan 50mg', 'Ibuprofen 600mg', 'Acetaminophen 1000mg'],
                'dosage': 'At onset of symptoms',
                'duration': 'Single dose, may repeat once',
                'instructions': 'Rest in dark, quiet room'
            },
            'Tension_Headache': {
                'medications': ['Acetaminophen 500mg', 'Ibuprofen 400mg', 'Aspirin 325mg'],
                'dosage': 'Every 6 hours as needed',
                'duration': '2-3 days maximum',
                'instructions': 'Apply heat/cold, gentle massage'
            },
            'Cluster_Headache': {
                'medications': ['Oxygen therapy', 'Sumatriptan injection', 'Verapamil 80mg'],
                'dosage': 'High-flow oxygen 15 min',
                'duration': 'During attack',
                'instructions': 'Seek neurologist for prevention plan'
            },
            'Vertigo': {
                'medications': ['Meclizine 25mg', 'Dimenhydrinate 50mg', 'Betahistine 16mg'],
                'dosage': 'Every 8 hours as needed',
                'duration': '3-7 days',
                'instructions': 'Avoid sudden movements, stay hydrated'
            },
            
            # Cardiovascular Conditions
            'Hypertension': {
                'medications': ['Lisinopril 10mg', 'Amlodipine 5mg', 'Hydrochlorothiazide 25mg'],
                'dosage': 'Once daily, same time',
                'duration': 'Long-term management',
                'instructions': 'Monitor blood pressure regularly'
            },
            'Angina': {
                'medications': ['Nitroglycerin 0.4mg', 'Metoprolol 50mg', 'Aspirin 81mg'],
                'dosage': 'Sublingual for chest pain',
                'duration': 'As prescribed',
                'instructions': 'Seek emergency care if pain persists'
            },
            'Heart_Attack': {
                'medications': ['Aspirin 325mg', 'Clopidogrel 75mg', 'Atorvastatin 40mg'],
                'dosage': 'EMERGENCY - Call 911',
                'duration': 'Hospital management',
                'instructions': 'Immediate emergency medical attention required'
            },
            
            # Infectious Diseases
            'Influenza': {
                'medications': ['Oseltamivir 75mg', 'Acetaminophen 500mg', 'Dextromethorphan'],
                'dosage': 'Twice daily for 5 days',
                'duration': '5-7 days',
                'instructions': 'Start within 48 hours of symptom onset'
            },
            'Strep_Throat': {
                'medications': ['Amoxicillin 500mg', 'Azithromycin 250mg', 'Cephalexin 500mg'],
                'dosage': 'Three times daily',
                'duration': '10 days',
                'instructions': 'Complete full antibiotic course'
            },
            'Mononucleosis': {
                'medications': ['Acetaminophen 500mg', 'Ibuprofen 400mg', 'Throat lozenges'],
                'dosage': 'Every 6 hours as needed',
                'duration': '2-4 weeks',
                'instructions': 'Rest, avoid contact sports for 6 weeks'
            },
            
            # Pain and Inflammation
            'Fibromyalgia': {
                'medications': ['Pregabalin 75mg', 'Duloxetine 30mg', 'Acetaminophen 500mg'],
                'dosage': 'Twice daily',
                'duration': 'Long-term management',
                'instructions': 'Regular exercise, stress management'
            },
            'Rheumatoid_Arthritis': {
                'medications': ['Methotrexate 15mg', 'Folic acid 5mg', 'Prednisone 10mg'],
                'dosage': 'Weekly (methotrexate)',
                'duration': 'Long-term management',
                'instructions': 'Regular blood monitoring required'
            },
            
            # Mental Health
            'Panic_Attack': {
                'medications': ['Lorazepam 0.5mg', 'Alprazolam 0.25mg', 'Propranolol 10mg'],
                'dosage': 'As needed for anxiety',
                'duration': 'Short-term use only',
                'instructions': 'Deep breathing, grounding techniques'
            },
            'Sleep_Apnea': {
                'medications': ['CPAP therapy', 'Modafinil 200mg', 'Melatonin 3mg'],
                'dosage': 'Nightly CPAP use',
                'duration': 'Long-term management',
                'instructions': 'Weight loss, avoid alcohol before bed'
            },
            
            # Chronic Conditions
            'Diabetes': {
                'medications': ['Metformin 500mg', 'Insulin (as prescribed)', 'Glipizide 5mg'],
                'dosage': 'With meals',
                'duration': 'Long-term management',
                'instructions': 'Monitor blood glucose regularly'
            },
            'Anemia': {
                'medications': ['Iron sulfate 325mg', 'Vitamin B12', 'Folic acid 5mg'],
                'dosage': 'Once daily with vitamin C',
                'duration': '3-6 months',
                'instructions': 'Take on empty stomach, monitor CBC'
            },
            'Chronic_Fatigue_Syndrome': {
                'medications': ['Modafinil 100mg', 'Vitamin D3', 'CoQ10 100mg'],
                'dosage': 'Morning dose',
                'duration': 'Long-term management',
                'instructions': 'Paced activity, adequate sleep'
            }
        }
        
        # Default recommendations for unknown conditions
        self.default_recommendations = {
            'medications': ['Acetaminophen 500mg', 'Ibuprofen 400mg', 'Plenty of rest'],
            'dosage': 'Follow package instructions',
            'duration': '3-5 days',
            'instructions': 'Consult healthcare provider if symptoms persist'
        }
    
    def get_recommendations(self, diagnosis: str) -> dict:
        """Get medication recommendations for a specific diagnosis"""
        
        # Clean up diagnosis name (remove underscores, handle variations)
        clean_diagnosis = diagnosis.replace('_', ' ').replace('-', ' ').title()
        
        # Direct match
        if diagnosis in self.medication_map:
            return self.medication_map[diagnosis]
        
        # Try variations
        for key in self.medication_map.keys():
            if key.lower().replace('_', ' ') == diagnosis.lower().replace('_', ' '):
                return self.medication_map[key]
        
        # Return default if no match found
        return self.default_recommendations
    
    def get_multiple_recommendations(self, diagnoses_list: list) -> dict:
        """Get recommendations for multiple diagnoses (top predictions)"""
        
        recommendations = {}
        for item in diagnoses_list:
            diagnosis = item.get('diagnosis', '')
            confidence = item.get('confidence', 0)
            
            med_info = self.get_recommendations(diagnosis)
            recommendations[diagnosis] = {
                'confidence': confidence,
                'medications': med_info['medications'],
                'dosage': med_info['dosage'],
                'duration': med_info['duration'],
                'instructions': med_info['instructions']
            }
        
        return recommendations
