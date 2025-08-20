import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

# Set up logging for training tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_training.log'),
        logging.StreamHandler()
    ]
)

class ContinuousLearningSystem:
    def __init__(self):
        self.learning_data_file = 'learning_data.json'
        self.feedback_data_file = 'feedback_data.json'
        self.unknown_cases_file = 'unknown_cases.json'
        self.training_history_file = 'training_history.json'
        
        # Initialize data storage files
        self._initialize_storage_files()
        
        # Load current model components
        try:
            self.model = joblib.load('diagnosis_model.pkl')
            self.label_encoder = joblib.load('label_encoder.pkl')
            self.feature_names = joblib.load('feature_names.pkl')
            logging.info("Existing model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            self.model = None
            self.label_encoder = None
            self.feature_names = None
    
    def _initialize_storage_files(self):
        """Initialize JSON files for storing learning data"""
        files = [
            self.learning_data_file,
            self.feedback_data_file, 
            self.unknown_cases_file,
            self.training_history_file
        ]
        
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump([], f)
                logging.info(f"Created {file}")
    
    def collect_prediction_data(self, symptoms, patient_data, prediction_result, user_feedback=None):
        """
        Collect prediction data for continuous learning
        """
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': symptoms,
            'patient_data': patient_data,
            'ai_prediction': prediction_result,
            'user_feedback': user_feedback,
            'confidence': prediction_result.get('confidence', 0),
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Store in learning data
        self._append_to_file(self.learning_data_file, learning_entry)
        logging.info(f"Collected learning data: {learning_entry['session_id']}")
        
        return learning_entry['session_id']
    
    def collect_feedback(self, session_id, actual_diagnosis, doctor_notes=None, treatment_outcome=None):
        """
        Collect feedback from healthcare providers or patient outcomes
        """
        feedback_entry = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'actual_diagnosis': actual_diagnosis,
            'doctor_notes': doctor_notes,
            'treatment_outcome': treatment_outcome,
            'feedback_type': 'professional' if doctor_notes else 'outcome'
        }
        
        self._append_to_file(self.feedback_data_file, feedback_entry)
        logging.info(f"Collected feedback for session: {session_id}")
        
        # Trigger retraining if enough feedback collected
        self._check_retraining_trigger()
    
    def handle_unknown_case(self, symptoms, patient_data, confidence_threshold=0.6):
        """
        Handle cases where AI confidence is low or symptoms don't match known patterns
        """
        unknown_entry = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': symptoms,
            'patient_data': patient_data,
            'reason': 'low_confidence' if confidence_threshold < 0.6 else 'unknown_pattern',
            'requires_human_review': True,
            'status': 'pending'
        }
        
        self._append_to_file(self.unknown_cases_file, unknown_entry)
        logging.info(f"Recorded unknown case for human review")
        
        return self._generate_unknown_case_response(symptoms, patient_data)
    
    def _generate_unknown_case_response(self, symptoms, patient_data):
        """
        Generate appropriate response for unknown cases
        """
        return {
            'status': 'unknown_case',
            'message': 'This symptom combination requires professional medical evaluation',
            'recommendation': 'immediate_medical_consultation',
            'reasoning': {
                'ai_limitation': 'The AI system does not have sufficient training data for this specific symptom combination.',
                'confidence_issue': 'The model confidence is below the threshold for reliable prediction.',
                'safety_protocol': 'For patient safety, professional medical evaluation is recommended.'
            },
            'suggested_actions': [
                'Schedule appointment with healthcare provider immediately',
                'Provide complete symptom list to medical professional',
                'Consider emergency care if symptoms are severe',
                'Do not delay seeking professional medical advice'
            ],
            'symptoms_provided': symptoms,
            'patient_age_group': self._get_age_group(patient_data.get('age', 0)),
            'risk_factors': patient_data.get('chronic_conditions', []),
            'urgent_care_indicators': self._check_urgent_indicators(symptoms),
            'medical_disclaimer': {
                'primary_message': '🚨 IMPORTANT: This case requires professional medical evaluation',
                'ai_limitation': 'The AI system cannot provide reliable diagnosis for this symptom pattern',
                'safety_requirement': 'Patient safety requires immediate professional consultation',
                'legal_notice': 'Do not delay seeking appropriate medical care'
            }
        }
    
    def retrain_model(self, include_feedback=True):
        """
        Retrain the model with new data and feedback
        """
        logging.info("Starting model retraining process...")
        
        try:
            # Load original training data
            original_data = pd.read_csv('symptoms_dataset.csv')
            
            # Load learning data and feedback
            new_training_data = self._prepare_training_data_from_feedback()
            
            if new_training_data is not None and len(new_training_data) > 0:
                # Combine original and new data
                combined_data = pd.concat([original_data, new_training_data], ignore_index=True)
                logging.info(f"Combined {len(original_data)} original + {len(new_training_data)} new samples")
            else:
                combined_data = original_data
                logging.info("No new training data available, using original data only")
            
            # Retrain model
            new_model, new_label_encoder, accuracy = self._train_model(combined_data)
            
            if accuracy > 0.4:  # Only update if reasonable accuracy
                # Backup old model
                self._backup_current_model()
                
                # Save new model
                joblib.dump(new_model, 'diagnosis_model.pkl')
                joblib.dump(new_label_encoder, 'label_encoder.pkl')
                joblib.dump(self.feature_names, 'feature_names.pkl')
                
                # Update instance variables
                self.model = new_model
                self.label_encoder = new_label_encoder
                
                # Record training history
                self._record_training_history(accuracy, len(combined_data))
                
                logging.info(f"Model retrained successfully. New accuracy: {accuracy:.2%}")
                return True
            else:
                logging.warning(f"Retraining failed. Low accuracy: {accuracy:.2%}")
                return False
                
        except Exception as e:
            logging.error(f"Error during retraining: {e}")
            return False
    
    def _prepare_training_data_from_feedback(self):
        """
        Prepare training data from collected feedback
        """
        try:
            # Load feedback data
            with open(self.feedback_data_file, 'r') as f:
                feedback_data = json.load(f)
            
            # Load learning data
            with open(self.learning_data_file, 'r') as f:
                learning_data = json.load(f)
            
            # Match feedback with learning data
            training_rows = []
            
            for feedback in feedback_data:
                # Find corresponding learning entry
                matching_learning = next(
                    (ld for ld in learning_data if ld['session_id'] == feedback['session_id']), 
                    None
                )
                
                if matching_learning and feedback.get('actual_diagnosis'):
                    # Create training row
                    symptoms = matching_learning['symptoms']
                    row = {feature: symptoms.get(feature, 0) for feature in self.feature_names}
                    row['diagnosis'] = feedback['actual_diagnosis']
                    training_rows.append(row)
            
            if training_rows:
                return pd.DataFrame(training_rows)
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error preparing training data: {e}")
            return None
    
    def _train_model(self, data):
        """
        Train model with given data
        """
        # Filter classes with sufficient samples
        class_counts = data['diagnosis'].value_counts()
        valid_classes = class_counts[class_counts >= 2].index
        filtered_data = data[data['diagnosis'].isin(valid_classes)]
        
        # Separate features and target
        X = filtered_data.drop('diagnosis', axis=1)
        y = filtered_data['diagnosis']
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        # Split data
        if len(filtered_data) > 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y_encoded, y_encoded
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Calculate accuracy
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return model, label_encoder, accuracy
    
    def _backup_current_model(self):
        """
        Backup current model before updating
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_files = [
            ('diagnosis_model.pkl', f'backup_model_{timestamp}.pkl'),
            ('label_encoder.pkl', f'backup_encoder_{timestamp}.pkl'),
            ('feature_names.pkl', f'backup_features_{timestamp}.pkl')
        ]
        
        for original, backup in backup_files:
            if os.path.exists(original):
                os.rename(original, backup)
                logging.info(f"Backed up {original} to {backup}")
    
    def _record_training_history(self, accuracy, data_size):
        """
        Record training history
        """
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy,
            'training_data_size': data_size,
            'model_version': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        self._append_to_file(self.training_history_file, history_entry)
    
    def _check_retraining_trigger(self):
        """
        Check if enough feedback has been collected to trigger retraining
        """
        try:
            with open(self.feedback_data_file, 'r') as f:
                feedback_data = json.load(f)
            
            # Check if we have enough new feedback (e.g., 10 new cases)
            recent_feedback = [
                fb for fb in feedback_data 
                if datetime.fromisoformat(fb['timestamp']) > datetime.now().replace(day=1)  # This month
            ]
            
            if len(recent_feedback) >= 10:
                logging.info(f"Retraining triggered: {len(recent_feedback)} new feedback cases")
                self.retrain_model()
                
        except Exception as e:
            logging.error(f"Error checking retraining trigger: {e}")
    
    def _append_to_file(self, filename, data):
        """
        Append data to JSON file
        """
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
            
            existing_data.append(data)
            
            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error appending to {filename}: {e}")
    
    def _get_age_group(self, age):
        """Get age group classification"""
        if age < 1:
            return 'infant'
        elif age < 12:
            return 'child'
        elif age < 18:
            return 'adolescent'
        elif age < 65:
            return 'adult'
        else:
            return 'elderly'
    
    def _check_urgent_indicators(self, symptoms):
        """Check for urgent care indicators"""
        urgent_symptoms = ['shortness_of_breath', 'chest_pain', 'severe_headache']
        return [symptom for symptom in urgent_symptoms if symptoms.get(symptom) == 1]
    
    def get_learning_statistics(self):
        """
        Get statistics about the learning system
        """
        try:
            stats = {}
            
            # Learning data stats
            with open(self.learning_data_file, 'r') as f:
                learning_data = json.load(f)
            stats['total_predictions'] = len(learning_data)
            
            # Feedback stats
            with open(self.feedback_data_file, 'r') as f:
                feedback_data = json.load(f)
            stats['feedback_received'] = len(feedback_data)
            
            # Unknown cases stats
            with open(self.unknown_cases_file, 'r') as f:
                unknown_data = json.load(f)
            stats['unknown_cases'] = len(unknown_data)
            
            # Training history
            with open(self.training_history_file, 'r') as f:
                history_data = json.load(f)
            stats['retraining_sessions'] = len(history_data)
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {}

# Initialize the learning system
learning_system = ContinuousLearningSystem()
