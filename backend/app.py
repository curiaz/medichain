#!/usr/bin/env python3
"""
MediChain Backend - Integrated with Streamlined AI v5.0
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import traceback
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re

# Lazy import sklearn to avoid Python 3.13 compatibility issues on startup
def _import_sklearn():
    """Lazy import sklearn components"""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        import joblib
        return RandomForestClassifier, LabelEncoder, train_test_split, accuracy_score, classification_report, joblib
    except Exception as e:
        print(f"⚠️ Warning: sklearn import failed: {e}")
        return None, None, None, None, None, None

from db.supabase_client import SupabaseClient

# Load environment variables
load_dotenv()

class StreamlinedAIDiagnosis:
    """Streamlined AI Diagnosis System using Supabase tables"""
    
    def __init__(self):
        """Initialize the streamlined diagnosis system"""
        self.model = None
        self.label_encoder = None
        self.symptom_columns = []
        self.conditions_df = None
        self.reasons_df = None
        self.actions_df = None
        self.model_version = "MediChain-Streamlined-v6.0-Supabase"
        self.supabase = SupabaseClient()
        
        print(f"🚀 Initializing {self.model_version}")
        self.load_data()
        self.train_model()
        print("✅ AI system ready!")
    
    def load_data(self):
        """Load all datasets from Supabase"""
        try:
            # Load main conditions dataset from Supabase
            print("📥 Fetching conditions from Supabase...")
            conditions_data = self.supabase.get_conditions()
            if not conditions_data:
                raise Exception("❌ No conditions data found in Supabase. Please ensure data is migrated to 'conditions' table.")
            self.conditions_df = pd.DataFrame(conditions_data)
            print(f"✅ Loaded conditions dataset: {len(self.conditions_df)} records")
            
            # Load reasons dataset from Supabase
            print("📥 Fetching condition reasons from Supabase...")
            reasons_data = self.supabase.get_condition_reasons()
            if not reasons_data:
                raise Exception("❌ No condition reasons found in Supabase. Please ensure data is migrated to 'condition_reasons' table.")
            self.reasons_df = pd.DataFrame(reasons_data)
            print(f"✅ Loaded reasons dataset: {len(self.reasons_df)} reasons")
            
            # Load actions/medications dataset from Supabase
            print("📥 Fetching action conditions from Supabase...")
            actions_data = self.supabase.get_action_conditions()
            if not actions_data:
                raise Exception("❌ No action conditions found in Supabase. Please ensure data is migrated to 'action_conditions' table.")
            self.actions_df = pd.DataFrame(actions_data)
            print(f"✅ Loaded actions/medications dataset: {len(self.actions_df)} entries")
            
            # Identify the key column and symptom columns
            first_col = self.conditions_df.columns[0]
            
            # Determine if first column is ID or condition name
            if first_col.lower() in ['id', 'condition_id', 'key']:
                self.id_column = first_col
                self.diagnosis_column = self.conditions_df.columns[1] if len(self.conditions_df.columns) > 1 else 'diagnosis'
                print(f"✅ Using ID-based linking: {self.id_column}")
            else:
                self.id_column = None
                self.diagnosis_column = first_col if first_col in ['condition', 'diagnosis'] else 'condition'
                print(f"✅ Using name-based linking: {self.diagnosis_column}")
            
            # Identify symptom columns (exclude ID and diagnosis columns)
            exclude_cols = {self.diagnosis_column}
            if self.id_column:
                exclude_cols.add(self.id_column)
            
            self.symptom_columns = [col for col in self.conditions_df.columns if col not in exclude_cols]
            print(f"✅ Identified {len(self.symptom_columns)} symptom features")
            
            # Validate data consistency
            self._validate_data_consistency()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def _validate_data_consistency(self):
        """Validate that all datasets can be properly linked"""
        try:
            conditions_set = set(self.conditions_df[self.diagnosis_column].values)
            
            # Check reasons dataset linking
            reasons_key_col = 'condition' if 'condition' in self.reasons_df.columns else self.reasons_df.columns[0]
            reasons_set = set(self.reasons_df[reasons_key_col].values)
            
            # Check actions dataset linking  
            actions_key_col = 'diagnosis' if 'diagnosis' in self.actions_df.columns else self.actions_df.columns[0]
            actions_set = set(self.actions_df[actions_key_col].values)
            
            # Find common conditions across all datasets
            common_conditions = conditions_set.intersection(reasons_set).intersection(actions_set)
            
            print(f"📊 Dataset validation:")
            print(f"   Conditions dataset: {len(conditions_set)} conditions")
            print(f"   Reasons dataset: {len(reasons_set)} conditions") 
            print(f"   Actions dataset: {len(actions_set)} conditions")
            print(f"   Common conditions: {len(common_conditions)} conditions")
            
            if len(common_conditions) < len(conditions_set) * 0.8:  # Less than 80% overlap
                print("⚠️  Warning: Low overlap between datasets. Some conditions may not have complete information.")
            
            # Store key column names for later use
            self.reasons_key_col = reasons_key_col
            self.actions_key_col = actions_key_col
            
        except Exception as e:
            print(f"⚠️  Warning: Could not validate data consistency: {e}")
    
    def train_model(self):
        """Train the AI model"""
        try:
            print("🔄 Training AI model...")
            
            # Lazy import sklearn
            RandomForestClassifier, LabelEncoder, train_test_split, accuracy_score, classification_report, joblib = _import_sklearn()
            if not RandomForestClassifier:
                raise Exception("sklearn import failed - cannot train model")
            
            # Prepare features and labels
            X = self.conditions_df[self.symptom_columns].values
            y = self.conditions_df[self.diagnosis_column].values
            
            print(f"📊 Dataset info: {len(X)} samples, {len(set(y))} classes")
            print(f"📊 Min class count: {min(pd.Series(y).value_counts())}")
            
            # Use all data for training since we have limited samples
            print("⚠️  Small dataset: training on all data")
            X_train, y_train = X, y
            
            # Initialize and train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            
            # Initialize label encoder
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y_train)
            
            # Train model
            self.model.fit(X_train, y_encoded)
            
            # Calculate accuracy
            y_pred = self.model.predict(X_train)
            accuracy = accuracy_score(y_encoded, y_pred)
            
            print("✅ Model trained successfully!")
            print(f"📊 Accuracy: {accuracy:.3f}")
            print(f"🎯 Classes: {len(self.label_encoder.classes_)}")
            
            # Save model with new version name
            model_path = os.path.join(os.path.dirname(__file__), 'supabase_model_v6.pkl')
            joblib.dump({
                'model': self.model,
                'label_encoder': self.label_encoder,
                'symptom_columns': self.symptom_columns,
                'version': self.model_version,
                'data_source': 'supabase'
            }, model_path)
            print(f"✅ Model saved: {os.path.basename(model_path)}")
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            raise
    
    def normalize_symptom(self, symptom_text: str) -> str:
        """Normalize symptom text to match CSV columns"""
        symptom_text = symptom_text.lower().strip()
        
        # Common normalizations
        normalizations = {
            'runny nose' : 'runny_nose',
            'sore throat': 'sore_throat',
            'back pain': 'back_pain',
            'neck pain': 'neck_pain',
            'ear pain': 'ear_pain',
            'tooth pain': 'tooth_pain',
            'muscle pain': 'muscle_pain',
            'joint pain': 'joint_pain',
            'chest pain': 'chest_pain',
            'abdominal pain': 'abdominal_pain',
            'shortness of breath': 'shortness_of_breath',
            'difficulty breathing': 'shortness_of_breath',
            'loss of appetite': 'loss_of_appetite',
            'weight loss': 'weight_loss',
            'weight gain': 'weight_gain',
            'high blood pressure': 'high_blood_pressure',
            'low blood pressure': 'low_blood_pressure',
            'rapid heartbeat': 'rapid_heartbeat',
            'slow heartbeat': 'slow_heartbeat',
            'blurred vision': 'blurred_vision',
            'burning sensation': 'burning_sensation',
            'itchy skin': 'itchy_skin',
            'dry skin': 'dry_skin',
            'frequent urination': 'frequent_urination',
            'painful urination': 'painful_urination',
            'loss of smell': 'loss_of_smell',
            'loss of taste': 'loss_of_taste',
            'dry cough': 'dry_cough',
            'productive cough': 'productive_cough',
            'difficulty swallowing': 'difficulty_swallowing',
            'itchy eyes': 'itchy_eyes',
            'watery eyes': 'watery_eyes',
            'night sweats': 'night_sweats',
            'cold hands feet': 'cold_hands_feet',
            'swollen lymph nodes': 'swollen_lymph_nodes',
            'pale skin': 'pale_skin',
            'yellow skin': 'yellow_skin',
            'dry mouth': 'dry_mouth',
            'bad breath': 'bad_breath',
            'acid reflux': 'acid_reflux',
            'nasal congestion': 'nasal_congestion',
            'postnasal drip': 'postnasal_drip',
            'post nasal drip': 'postnasal_drip',  # Added normalization for spaced version
            'labored breathing': 'labored_breathing',
            'loss of concentration': 'loss_of_concentration',
            'tight chest': 'tight_chest',
            'mucus production': 'mucus_production',
            'itchy throat': 'itchy_throat',
            'sensitivity to light': 'sensitivity_to_light',
            'stiff neck': 'stiff_neck',
            'chills without fever': 'chills_without_fever',
            'burning eyes': 'burning_eyes',
            'ear discharge': 'ear_discharge',
            'skin peeling': 'skin_peeling',
            'scalp itchiness': 'scalp_itchiness',
            'mood swings': 'mood_swings',
            'itchy scalp': 'scalp_itchiness',
            'itching scalp': 'scalp_itchiness'
        }
        
        # Apply normalizations
        normalized = normalizations.get(symptom_text, symptom_text)
        
        # Replace spaces with underscores
        normalized = normalized.replace(' ', '_')
        
        return normalized
    
    def parse_symptoms(self, symptoms_text: str) -> Dict[str, int]:
        """Parse symptoms from natural language text"""
        # Initialize all symptoms to 0
        detected_symptoms = {col: 0 for col in self.symptom_columns}
        
        # Clean and normalize input
        symptoms_text = symptoms_text.lower()
        
        # Remove common phrases
        symptoms_text = re.sub(r'i have|i am experiencing|i feel|symptoms include|suffering from', '', symptoms_text)
        
        # Split by common delimiters
        symptom_phrases = re.split(r'[,;.]|\sand\s|\sor\s', symptoms_text)
        
        # Process each phrase
        for phrase in symptom_phrases:
            phrase = phrase.strip()
            if not phrase:
                continue
            
            # Try to match against symptom columns
            normalized_phrase = self.normalize_symptom(phrase)
            
            # Direct match
            if normalized_phrase in self.symptom_columns:
                detected_symptoms[normalized_phrase] = 1
                continue
            
            # Partial matches
            for symptom in self.symptom_columns:
                if symptom in normalized_phrase or normalized_phrase in symptom:
                    detected_symptoms[symptom] = 1
                    break
        
        return detected_symptoms
    
    def predict_conditions(self, symptoms_text: str) -> List[Dict]:
        """Predict top 3 conditions based on direct symptom matching"""
        try:
            # Parse symptoms from text
            symptom_flags = self.parse_symptoms(symptoms_text)
            active_symptoms = [sym for sym, val in symptom_flags.items() if val == 1]
            
            if len(active_symptoms) == 0:
                return []
            
            # Calculate match scores for all conditions
            condition_scores = []
            
            for idx, row in self.conditions_df.iterrows():
                condition = row[self.diagnosis_column]
                matches = 0
                condition_symptom_count = 0
                
                # Count symptom matches
                for symptom in active_symptoms:
                    if symptom in row and row[symptom] == 1:
                        matches += 1
                
                # Count total symptoms this condition has
                for col in self.symptom_columns:
                    if row[col] == 1:
                        condition_symptom_count += 1
                
                if matches > 0:  # Only consider conditions with at least one match
                    # Calculate match percentage
                    match_percentage = (matches / len(active_symptoms)) * 100
                    
                    # Calculate precision (how many of the condition's symptoms match)
                    precision = (matches / condition_symptom_count) * 100 if condition_symptom_count > 0 else 0
                    
                    # Enhanced symptom matching with category bonuses
                    respiratory_symptoms = {'cough', 'runny_nose', 'sore_throat', 'sneezing', 'nasal_congestion', 'postnasal_drip', 'hoarseness'}
                    gastrointestinal_symptoms = {'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'bloating', 'constipation', 'heartburn'}
                    neurological_symptoms = {'headache', 'dizziness', 'confusion', 'blurred_vision', 'numbness', 'tingling'}
                    musculoskeletal_symptoms = {'back_pain', 'neck_pain', 'muscle_pain', 'joint_pain', 'weakness'}
                    systemic_symptoms = {'fever', 'fatigue', 'chills', 'sweating', 'weight_loss', 'weight_gain'}
                    
                    # Condition categories for bonuses
                    respiratory_conditions = {'Common Cold', 'COVID-19 (Mild)', 'Flu (Influenza)', 'Upper Respiratory Infection', 
                                           'Sinus Infection', 'Bronchitis', 'Allergic Rhinitis', 'Asthma'}
                    gastrointestinal_conditions = {'Acid Reflux', 'Indigestion (Dyspepsia)', 'Stomach Flu', 'Food Poisoning', 
                                                 'Gastritis', 'Gastroenteritis'}
                    
                    category_bonus = 0
                    
                    # Calculate category-specific bonuses
                    user_respiratory_symptoms = [s for s in active_symptoms if s in respiratory_symptoms]
                    user_gi_symptoms = [s for s in active_symptoms if s in gastrointestinal_symptoms]
                    user_neuro_symptoms = [s for s in active_symptoms if s in neurological_symptoms]
                    
                    # Respiratory bonus
                    if len(user_respiratory_symptoms) >= 2 and condition in respiratory_conditions:
                        if condition in {'Common Cold', 'COVID-19 (Mild)', 'Flu (Influenza)'}:
                            category_bonus += 25  # Higher boost for primary respiratory conditions
                        else:
                            category_bonus += 15
                    elif len(user_respiratory_symptoms) >= 1 and condition in respiratory_conditions:
                        category_bonus += 10
                    
                    # Gastrointestinal bonus
                    if len(user_gi_symptoms) >= 2 and condition in gastrointestinal_conditions:
                        category_bonus += 20
                    elif len(user_gi_symptoms) >= 1 and condition in gastrointestinal_conditions:
                        category_bonus += 8
                    
                    # Multi-system condition handling (conditions that span multiple categories)
                    multi_system_conditions = {'Flu (Influenza)', 'COVID-19 (Mild)', 'Food Poisoning'}
                    if condition in multi_system_conditions:
                        # Additional bonus for conditions that naturally affect multiple systems
                        if len(user_respiratory_symptoms) >= 1 and len(user_gi_symptoms) >= 1:
                            category_bonus += 10
                        elif len(user_neuro_symptoms) >= 1 and (len(user_respiratory_symptoms) >= 1 or len(user_gi_symptoms) >= 1):
                            category_bonus += 8
                    
                    # Combined score: prioritize match percentage, then precision, plus category bonus
                    combined_score = (match_percentage * 0.6) + (precision * 0.2) + category_bonus
                    
                    # Penalty for conditions with too many unmatched symptoms (over-specific conditions)
                    if condition_symptom_count > len(active_symptoms) * 2:
                        penalty = min(10, (condition_symptom_count - len(active_symptoms)) * 0.5)
                        combined_score -= penalty
                    
                    condition_scores.append({
                        'condition': condition,
                        'matches': matches,
                        'total_user_symptoms': len(active_symptoms),
                        'match_percentage': match_percentage,
                        'precision': precision,
                        'combined_score': combined_score,
                        'condition_symptom_count': condition_symptom_count
                    })
            
            # Sort by combined score (highest first)
            condition_scores.sort(key=lambda x: -x['combined_score'])
            
            # Return top 3 predictions
            predictions = []
            for i, score in enumerate(condition_scores[:3]):
                predictions.append({
                    'rank': i + 1,
                    'condition': score['condition'],
                    'confidence': score['combined_score'] / 100,  # Convert to 0-1 scale
                    'confidence_percent': f"{score['combined_score']:.1f}%",
                    'matches': score['matches'],
                    'total_symptoms': score['total_user_symptoms'],
                    'match_details': f"{score['matches']}/{score['total_user_symptoms']} symptoms ({score['match_percentage']:.1f}%)"
                })
            
            return predictions
            
        except Exception as e:
            print(f"❌ Error predicting conditions: {e}")
            return []
    
    def get_condition_reason(self, condition: str) -> str:
        """Get the reason/explanation for a condition - ONLY from CSV data"""
        try:
            reason_row = self.reasons_df[self.reasons_df[self.reasons_key_col] == condition]
            if not reason_row.empty:
                reason_col = 'reason' if 'reason' in self.reasons_df.columns else self.reasons_df.columns[1]
                return reason_row.iloc[0][reason_col]
            return f"[No reason data available in CSV for: {condition}]"
        except Exception as e:
            print(f"❌ Error getting condition reason: {e}")
            return f"[Error retrieving reason for: {condition}]"
    
    def get_recommended_action_and_medication(self, condition: str) -> Dict:
        """Get recommended action and medication for a condition"""
        try:
            action_row = self.actions_df[self.actions_df[self.actions_key_col] == condition]
            if not action_row.empty:
                row = action_row.iloc[0]
                
                # Map possible column names to standard keys
                col_mapping = {
                    'recommended_action': ['recommended_action', 'action', 'treatment'],
                    'medication': ['medication', 'medicine', 'drug'],
                    'dosage': ['dosage', 'dose', 'adult_dose'],
                    'notes': ['notes', 'note', 'description']
                }
                
                result = {}
                for key, possible_cols in col_mapping.items():
                    for col in possible_cols:
                        if col in row and pd.notna(row[col]) and str(row[col]).strip():
                            result[key] = str(row[col]).strip()
                            break
                    if key not in result:
                        result[key] = f"[No {key} data in CSV for: {condition}]"
                
                return result
            
            return {
                'recommended_action': f'[No action data in CSV for: {condition}]',
                'medication': f'[No medication data in CSV for: {condition}]',
                'dosage': f'[No dosage data in CSV for: {condition}]',
                'notes': f'[No notes data in CSV for: {condition}]'
            }
        except Exception as e:
            print(f"❌ Error getting action/medication: {e}")
            return {
                'recommended_action': f'[Error retrieving action for: {condition}]',
                'medication': f'[Error retrieving medication for: {condition}]',
                'dosage': f'[Error retrieving dosage for: {condition}]',
                'notes': f'[Error retrieving notes for: {condition}]'
            }
    
    def diagnose(self, symptoms_text: str) -> Dict:
        """Main diagnosis function"""
        try:
            print(f"🩺 Processing symptoms: {symptoms_text}")
            
            # Parse symptoms first to get detected symptoms for slide 1
            symptom_flags = self.parse_symptoms(symptoms_text)
            detected_symptoms = [sym.replace('_', ' ').title() for sym, val in symptom_flags.items() if val == 1]
            
            # Get predictions
            predictions = self.predict_conditions(symptoms_text)
            
            if not predictions:
                return {
                    'success': False,
                    'message': 'Unable to identify conditions from the provided symptoms',
                    'data': None
                }
            
            # Get detailed information for each prediction with enhanced medication data
            detailed_results = []
            for pred in predictions:
                condition = pred['condition']
                reason = self.get_condition_reason(condition)
                action_info = self.get_recommended_action_and_medication(condition)
                
                # Get full medication information from CSV
                medication_row = self.actions_df[self.actions_df[self.actions_key_col] == condition]
                medication_details = {}
                
                if not medication_row.empty:
                    row = medication_row.iloc[0]
                    medication_details = {
                        'medicine': str(row.get('medicine', '')).strip() if pd.notna(row.get('medicine')) else f'[No medicine data in CSV for: {condition}]',
                        'adult_dose': str(row.get('adult_dose', '')).strip() if pd.notna(row.get('adult_dose')) else f'[No adult dose data in CSV for: {condition}]',
                        'child_dose': str(row.get('child_dose', '')).strip() if pd.notna(row.get('child_dose')) else f'[No child dose data in CSV for: {condition}]',
                        'max_daily_dose': str(row.get('max_daily_dose', '')).strip() if pd.notna(row.get('max_daily_dose')) else f'[No max dose data in CSV for: {condition}]',
                        'description': str(row.get('description', '')).strip() if pd.notna(row.get('description')) else f'[No description data in CSV for: {condition}]',
                        'notes': str(row.get('notes', '')).strip() if pd.notna(row.get('notes')) else f'[No notes data in CSV for: {condition}]'
                    }
                else:
                    medication_details = {
                        'medicine': f'[No medication row found in CSV for: {condition}]',
                        'adult_dose': f'[No adult dose found in CSV for: {condition}]',
                        'child_dose': f'[No child dose found in CSV for: {condition}]',
                        'max_daily_dose': f'[No max dose found in CSV for: {condition}]',
                        'description': f'[No description found in CSV for: {condition}]',
                        'notes': f'[No notes found in CSV for: {condition}]'
                    }
                
                detailed_results.append({
                    'condition': condition,
                    'confidence': pred['confidence_percent'],
                    'reason': reason,
                    'recommended_action': action_info['recommended_action'],
                    'medication': action_info['medication'],
                    'dosage': action_info['dosage'],
                    'notes': action_info['notes'],
                    'match_details': pred['match_details'],
                    'medication_details': medication_details
                })
            
            return {
                'success': True,
                'message': 'Diagnosis completed successfully',
                'data': {
                    'detected_symptoms': detected_symptoms,
                    'primary_condition': predictions[0]['condition'],
                    'primary_confidence': predictions[0]['confidence_percent'],
                    'detailed_results': detailed_results,
                    'disclaimer': 'This is an AI-generated diagnosis. Always consult with a qualified healthcare provider for proper medical evaluation and treatment.'
                }
            }
            
        except Exception as e:
            print(f"❌ Error in diagnosis: {e}")
            return {
                'success': False,
                'message': f'Diagnosis error: {str(e)}',
                'data': None
            }

# Initialize Flask app
app = Flask(__name__)

# Register authentication blueprint
from auth.auth_routes import auth_bp
from doctor_verification import doctor_verification_bp
try:
    from notifications.notification_routes_supabase import notifications_bp
    print("✅ Using Supabase notification routes")
except ImportError:
    # Fallback to SQLite version if Supabase version not available
    from notifications.notification_routes import notifications_bp
    print("⚠️  Using SQLite notification routes (fallback)")
from appointment_routes import appointments_bp
from admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(doctor_verification_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(admin_bp)

# 🔧 FIXED: CORS configuration with credentials support (removed "*" to fix CORS issues)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# 🆕 Handle preflight OPTIONS requests
@app.before_request
def handle_preflight():
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get("Origin", "http://localhost:3000")
        # Only allow whitelisted origins
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ]
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

# 🆕 Global error handler to prevent crashes without response
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions gracefully"""
    print(f"❌ Unhandled exception: {e}")
    traceback.print_exc()
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": str(e)
    }), 500

# Initialize AI system
print("🚀 Starting Streamlined MediChain API v5.0...")
print("=" * 60)
ai_engine = None

try:
    ai_engine = StreamlinedAIDiagnosis()
    print("✅ AI system initialized successfully!")
except Exception as e:
    print(f"⚠️  AI system initialization failed: {e}")
    print("⚠️  Server will continue but AI endpoints will return 503")
    # 🔧 FIXED: Don't exit - let server run so health endpoints can respond

# Routes
@app.route('/')
def home():
    """Home route"""
    return jsonify({
        'message': 'MediChain API v5.0 - Streamlined',
        'status': 'active',
        'ai_system': ai_engine.model_version if ai_engine else 'unavailable',
        'endpoints': {
            'health': '/health',
            'ai_health': '/api/ai/health', 
            'diagnose': '/api/diagnose',
            'symptom_explanations': '/api/symptom-explanations'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': pd.Timestamp.now().isoformat(),
        'ai_system': ai_engine.model_version if ai_engine else 'unavailable'
    })

@app.route('/api/ai/health', methods=['GET'])
def ai_health():
    """AI system health check"""
    if not ai_engine:
        return jsonify({
            'status': 'error',
            'message': 'AI system not initialized'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'ai_system': ai_engine.model_version,
        'conditions_loaded': len(ai_engine.conditions_df),
        'symptoms_tracked': len(ai_engine.symptom_columns)
    })

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Main diagnosis endpoint"""
    try:
        if not ai_engine:
            return jsonify({
                'success': False,
                'message': 'AI system not available'
            }), 503
        
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing symptoms in request'
            }), 400
        
        symptoms = data['symptoms']
        if not symptoms or not symptoms.strip():
            return jsonify({
                'success': False,
                'message': 'Empty symptoms provided'
            }), 400
        
        # Run diagnosis
        result = ai_engine.diagnose(symptoms.strip())
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in /api/diagnose: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/symptom-explanations', methods=['POST'])
def symptom_explanations():
    """Get explanations for detected symptoms"""
    try:
        if not ai_engine:
            return jsonify({
                'success': False,
                'message': 'AI system not available'
            }), 503
        
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing symptoms in request'
            }), 400
        
        symptoms_text = data['symptoms']
        
        # Parse symptoms
        parsed_symptoms = ai_engine.parse_symptoms(symptoms_text)
        detected_symptoms = [sym for sym, val in parsed_symptoms.items() if val == 1]
        
        return jsonify({
            'success': True,
            'data': {
                'detected_symptoms': detected_symptoms,
                'total_detected': len(detected_symptoms),
                'symptom_details': {sym: 'Detected symptom' for sym in detected_symptoms}
            }
        })
        
    except Exception as e:
        print(f"❌ Error in /api/symptom-explanations: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🌐 Starting Flask server...")
    print(f"📡 API available at: http://localhost:5000")
    print(f"🩺 Diagnosis endpoint: POST /api/diagnose")
    print(f"📋 Explanations endpoint: POST /api/symptom-explanations")
    print(f"❤️  Health check: GET /health")
    print("=" * 60)
    
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000
    )