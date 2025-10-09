from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import csv
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# NLP-only AI Diagnosis Engine (no ML dependencies)
class NLPAIEngine:
    def __init__(self):
        self.dataset = []
        self.symptom_columns = []
        self.diagnoses = set()
        self.diagnosis_info = {}
        self.load_dataset()
        self.create_diagnosis_patterns()
    
    def load_dataset(self):
        """Load the enhanced dataset"""
        dataset_path = os.path.join(os.path.dirname(__file__), 'final_enhanced_dataset.csv')
        
        try:
            with open(dataset_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                self.dataset = list(csv_reader)
                
                if self.dataset:
                    # Get symptom columns (excluding 'Diagnosis')
                    all_columns = list(self.dataset[0].keys())
                    self.symptom_columns = [col for col in all_columns if col != 'Diagnosis']
                    
                    # Collect all unique diagnoses
                    for row in self.dataset:
                        if row.get('Diagnosis'):
                            self.diagnoses.add(row['Diagnosis'])
                    
                    print(f"✅ Dataset loaded: {len(self.dataset)} records, {len(self.symptom_columns)} symptoms, {len(self.diagnoses)} conditions")
                
        except FileNotFoundError:
            print("❌ Dataset file not found. Using fallback diagnosis list.")
            self.diagnoses = {'Common Cold', 'Flu', 'Migraine', 'Anxiety', 'Depression'}
            self.symptom_columns = ['fever', 'headache', 'cough', 'fatigue', 'nausea']
    
    def create_diagnosis_patterns(self):
        """Create NLP patterns for condition extraction"""
        self.condition_patterns = {
            # Respiratory conditions
            'asthma': ['asthma', 'wheezing', 'shortness of breath', 'breathing difficulty', 'chest tightness'],
            'bronchitis': ['bronchitis', 'persistent cough', 'chest congestion', 'mucus', 'respiratory infection'],
            'pneumonia': ['pneumonia', 'lung infection', 'chest pain when breathing', 'fever with cough', 'difficulty breathing'],
            'common cold': ['cold', 'runny nose', 'sneezing', 'stuffy nose', 'mild fever', 'throat irritation'],
            'flu': ['flu', 'influenza', 'body aches', 'high fever', 'chills', 'severe fatigue'],
            
            # Cardiovascular
            'hypertension': ['high blood pressure', 'hypertension', 'elevated pressure', 'blood pressure'],
            'heart disease': ['heart disease', 'cardiac', 'chest pain', 'heart attack', 'coronary'],
            
            # Neurological
            'migraine': ['migraine', 'severe headache', 'throbbing head pain', 'light sensitivity', 'nausea with headache'],
            'tension headache': ['tension headache', 'head pressure', 'stress headache', 'tight band feeling'],
            
            # Mental Health
            'anxiety': ['anxiety', 'panic', 'worry', 'nervousness', 'restlessness', 'racing thoughts'],
            'depression': ['depression', 'sadness', 'hopelessness', 'low mood', 'loss of interest'],
            
            # Gastrointestinal
            'gastritis': ['gastritis', 'stomach inflammation', 'stomach pain', 'indigestion', 'stomach burning'],
            'acid reflux': ['acid reflux', 'heartburn', 'gerd', 'chest burning', 'stomach acid'],
            
            # Musculoskeletal
            'arthritis': ['arthritis', 'joint pain', 'joint stiffness', 'joint swelling', 'inflammatory joint'],
            'back pain': ['back pain', 'lower back', 'spine pain', 'back stiffness'],
            
            # Endocrine
            'diabetes': ['diabetes', 'high blood sugar', 'glucose', 'insulin', 'diabetic'],
            'thyroid disorder': ['thyroid', 'hyperthyroid', 'hypothyroid', 'thyroid gland'],
            
            # Others
            'allergic reaction': ['allergy', 'allergic', 'rash', 'hives', 'allergic reaction', 'itching'],
            'skin condition': ['skin rash', 'dermatitis', 'eczema', 'skin irritation', 'skin problem'],
            'urinary tract infection': ['uti', 'urinary infection', 'bladder infection', 'burning urination'],
            'sleep disorder': ['insomnia', 'sleep problems', 'sleep disorder', 'difficulty sleeping'],
            'fatigue syndrome': ['chronic fatigue', 'extreme tiredness', 'persistent fatigue', 'exhaustion']
        }
    
    def extract_conditions_from_text(self, text):
        """Extract potential conditions from text using NLP patterns"""
        text_lower = text.lower()
        matched_conditions = []
        
        for condition, patterns in self.condition_patterns.items():
            matches = []
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    matches.append(pattern)
            
            if matches:
                matched_conditions.append({
                    'condition': condition,
                    'matched_keywords': matches,
                    'pattern_matches': len(matches)
                })
        
        # Sort by number of pattern matches (most relevant first)
        matched_conditions.sort(key=lambda x: x['pattern_matches'], reverse=True)
        
        return matched_conditions
    
    def predict_nlp_diagnosis(self, symptoms_text, patient_conditions=None):
        """Generate diagnosis using NLP-based condition extraction"""
        try:
            # Extract conditions from symptoms text
            extracted_conditions = self.extract_conditions_from_text(symptoms_text)
            
            if not extracted_conditions:
                # Fallback to common conditions if no specific matches
                extracted_conditions = [
                    {'condition': 'viral infection', 'matched_keywords': ['general symptoms'], 'pattern_matches': 1},
                    {'condition': 'stress related condition', 'matched_keywords': ['multiple symptoms'], 'pattern_matches': 1}
                ]
            
            # Prepare primary diagnosis
            primary_condition = extracted_conditions[0]
            
            # Create diagnosis result structure
            result = {
                'diagnosis': primary_condition['condition'].title(),
                'reasoning': f"Based on keyword analysis: {', '.join(primary_condition['matched_keywords'])}",
                'extraction_method': 'NLP Pattern Matching',
                'matched_patterns': primary_condition['pattern_matches'],
                'top_predictions': [],
                'detected_symptoms': {},
                'analysis_summary': f"Identified {len(extracted_conditions)} potential conditions from symptom description"
            }
            
            # Add top predictions with reasoning
            for i, condition in enumerate(extracted_conditions[:5]):
                result['top_predictions'].append({
                    'diagnosis': condition['condition'].title(),
                    'reasoning': f"Matched keywords: {', '.join(condition['matched_keywords'])}",
                    'relevance_score': condition['pattern_matches']
                })
            
            # Extract symptoms mentioned in text
            symptom_keywords = [
                'fever', 'headache', 'cough', 'fatigue', 'nausea', 'vomiting', 'diarrhea',
                'pain', 'swelling', 'rash', 'itching', 'dizziness', 'weakness', 'sweating'
            ]
            
            for symptom in symptom_keywords:
                if symptom.lower() in symptoms_text.lower():
                    result['detected_symptoms'][symptom] = 1
            
            return result
            
        except Exception as e:
            print(f"Error in NLP diagnosis: {str(e)}")
            return {
                'diagnosis': 'Unable to determine',
                'reasoning': 'Analysis failed due to processing error',
                'extraction_method': 'Error',
                'matched_patterns': 0,
                'top_predictions': [],
                'detected_symptoms': {},
                'analysis_summary': f"Error during analysis: {str(e)}"
            }

# Initialize AI engine
ai_diagnosis_engine = NLPAIEngine()

@app.route('/api/ai/diagnose', methods=['POST'])
def ai_diagnose():
    """Enhanced AI diagnosis endpoint with NLP extraction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract symptoms and patient info
        symptoms = data.get('symptoms', '')
        patient_age = data.get('patientAge', '')
        patient_gender = data.get('patientGender', '')
        
        if not symptoms:
            return jsonify({
                'success': False,
                'error': 'Symptoms are required'
            }), 400
        
        # Prepare full text for analysis
        full_text = symptoms
        if patient_age:
            full_text += f" Patient age: {patient_age}"
        if patient_gender:
            full_text += f" Gender: {patient_gender}"
        
        # Patient conditions for context
        patient_conditions = {
            'age': patient_age,
            'gender': patient_gender
        }
        
        result = ai_diagnosis_engine.predict_nlp_diagnosis(
            full_text or symptoms,
            patient_conditions
        )
        
        # Format response for frontend
        response_data = {
            'success': True,
            'analysis': {
                'diagnosis_data': result,
                'slides': [
                    {
                        'type': 'symptoms',
                        'title': 'Symptoms Reported',
                        'content': symptoms,
                        'patientAge': patient_age,
                        'patientGender': patient_gender
                    },
                    {
                        'type': 'conditions',
                        'title': 'Possible Conditions',
                        'content': f"Analysis using {result.get('extraction_method', 'NLP')}",
                        'diagnosisData': result
                    },
                    {
                        'type': 'severity',
                        'title': 'Assessment Notes',
                        'content': f"• {result.get('analysis_summary', 'Analysis completed')}\n• Method: {result.get('extraction_method', 'NLP Pattern Matching')}\n• Patterns matched: {result.get('matched_patterns', 0)}"
                    },
                    {
                        'type': 'recommendations',
                        'title': 'Recommended Actions',
                        'content': "• Consult with a healthcare professional for proper diagnosis\n• Monitor symptoms and note any changes\n• This analysis is for informational purposes only"
                    }
                ]
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Diagnosis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MediChain AI NLP Server',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0-NLP'
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"🚀 Starting MediChain AI NLP Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)