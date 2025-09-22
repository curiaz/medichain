#!/usr/bin/env python3
"""
Final Model Training Script for MediChain Comprehensive AI
Trains the comprehensive model with 985 samples and 56 diagnoses
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import pickle
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_training_data():
    """Load and prepare comprehensive training dataset"""
    
    # Comprehensive medical diagnoses with symptoms, duration, and intensity
    data = [
        # Respiratory Conditions
        ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'chest_pain', '', '', '', '', '', '', '', '', '', 5, 2, 'Pneumonia'],
        ['cough', 'fever', 'fatigue', 'body_aches', 'chest_pain', '', '', '', '', '', '', '', '', '', 7, 2, 'Bronchitis'],
        ['shortness_of_breath', 'chest_pain', 'fatigue', 'dizziness', '', '', '', '', '', '', '', '', '', '', 3, 3, 'Asthma_Attack'],
        ['fever', 'cough', 'sore_throat', 'runny_nose', 'headache', 'body_aches', '', '', '', '', '', '', '', '', 5, 2, 'Upper_Respiratory_Infection'],
        ['fever', 'cough', 'shortness_of_breath', 'fatigue', 'loss_of_taste', 'loss_of_smell', '', '', '', '', '', '', '', '', 10, 2, 'COVID_19'],
        
        # Gastrointestinal Conditions
        ['nausea', 'diarrhea', 'fever', 'body_aches', 'fatigue', '', '', '', '', '', '', '', '', '', 3, 2, 'Gastroenteritis'],
        ['nausea', 'diarrhea', 'fever', 'headache', 'fatigue', '', '', '', '', '', '', '', '', '', 2, 3, 'Food_Poisoning'],
        ['nausea', 'chest_pain', 'dizziness', '', '', '', '', '', '', '', '', '', '', '', 1, 3, 'GERD'],
        
        # Neurological Conditions  
        ['headache', 'nausea', 'dizziness', 'fatigue', '', '', '', '', '', '', '', '', '', '', 1, 3, 'Migraine'],
        ['headache', 'fever', 'fatigue', 'body_aches', '', '', '', '', '', '', '', '', '', '', 2, 2, 'Tension_Headache'],
        ['dizziness', 'nausea', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 3, 2, 'Vertigo'],
        
        # Cardiovascular Conditions
        ['chest_pain', 'shortness_of_breath', 'dizziness', 'fatigue', '', '', '', '', '', '', '', '', '', '', 1, 3, 'Angina'],
        ['chest_pain', 'shortness_of_breath', 'nausea', 'dizziness', 'fatigue', '', '', '', '', '', '', '', '', '', 1, 3, 'Heart_Attack'],
        ['dizziness', 'fatigue', 'headache', '', '', '', '', '', '', '', '', '', '', '', 7, 1, 'Hypertension'],
        
        # Infectious Diseases
        ['fever', 'fatigue', 'body_aches', 'headache', 'sore_throat', '', '', '', '', '', '', '', '', '', 5, 2, 'Influenza'],
        ['fever', 'sore_throat', 'body_aches', 'headache', '', '', '', '', '', '', '', '', '', '', 7, 2, 'Strep_Throat'],
        ['fever', 'fatigue', 'headache', 'body_aches', '', '', '', '', '', '', '', '', '', '', 10, 2, 'Mononucleosis'],
        
        # Common Cold and Allergies
        ['runny_nose', 'sore_throat', 'cough', 'fatigue', '', '', '', '', '', '', '', '', '', '', 7, 1, 'Common_Cold'],
        ['runny_nose', 'cough', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 14, 1, 'Allergic_Rhinitis'],
        
        # Additional conditions to reach 56 diagnoses
        ['fatigue', 'body_aches', 'headache', '', '', '', '', '', '', '', '', '', '', '', 30, 1, 'Chronic_Fatigue_Syndrome'],
        ['headache', 'fatigue', 'dizziness', 'nausea', '', '', '', '', '', '', '', '', '', '', 1, 2, 'Cluster_Headache'],
        ['chest_pain', 'cough', 'fever', '', '', '', '', '', '', '', '', '', '', '', 5, 2, 'Pleurisy'],
        ['shortness_of_breath', 'chest_pain', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Pulmonary_Embolism'],
        ['fever', 'cough', 'fatigue', 'body_aches', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Tuberculosis'],
        ['dizziness', 'nausea', 'headache', 'fatigue', '', '', '', '', '', '', '', '', '', '', 3, 2, 'Inner_Ear_Infection'],
        ['sore_throat', 'fever', 'fatigue', 'body_aches', '', '', '', '', '', '', '', '', '', '', 5, 2, 'Tonsillitis'],
        ['runny_nose', 'headache', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 7, 1, 'Sinusitis'],
        ['cough', 'fever', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 21, 2, 'Whooping_Cough'],
        ['fever', 'headache', 'body_aches', 'fatigue', '', '', '', '', '', '', '', '', '', '', 7, 2, 'Malaria'],
        ['nausea', 'diarrhea', 'fever', '', '', '', '', '', '', '', '', '', '', '', 3, 2, 'Salmonella'],
        ['fatigue', 'fever', 'body_aches', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Hepatitis'],
        ['chest_pain', 'cough', 'fever', 'fatigue', '', '', '', '', '', '', '', '', '', '', 10, 2, 'Lung_Cancer'],
        ['headache', 'nausea', 'dizziness', '', '', '', '', '', '', '', '', '', '', '', 1, 3, 'Brain_Tumor'],
        ['fatigue', 'body_aches', 'fever', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Lupus'],
        ['body_aches', 'fatigue', 'headache', '', '', '', '', '', '', '', '', '', '', '', 30, 2, 'Fibromyalgia'],
        ['fever', 'fatigue', 'body_aches', 'headache', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Rheumatoid_Arthritis'],
        ['dizziness', 'fatigue', 'headache', '', '', '', '', '', '', '', '', '', '', '', 7, 1, 'Anemia'],
        ['fatigue', 'body_aches', 'dizziness', '', '', '', '', '', '', '', '', '', '', '', 30, 1, 'Diabetes'],
        ['chest_pain', 'shortness_of_breath', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Cardiomyopathy'],
        ['headache', 'dizziness', 'nausea', 'fatigue', '', '', '', '', '', '', '', '', '', '', 1, 2, 'Concussion'],
        ['fever', 'headache', 'body_aches', 'fatigue', '', '', '', '', '', '', '', '', '', '', 7, 2, 'Meningitis'],
        ['cough', 'fever', 'fatigue', 'chest_pain', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Sarcoidosis'],
        ['shortness_of_breath', 'fatigue', 'chest_pain', '', '', '', '', '', '', '', '', '', '', '', 21, 2, 'Pulmonary_Fibrosis'],
        ['nausea', 'diarrhea', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 7, 2, 'Crohns_Disease'],
        ['fatigue', 'body_aches', 'fever', '', '', '', '', '', '', '', '', '', '', '', 21, 2, 'Multiple_Sclerosis'],
        ['headache', 'fatigue', 'dizziness', '', '', '', '', '', '', '', '', '', '', '', 14, 1, 'Sleep_Apnea'],
        ['fever', 'cough', 'fatigue', 'body_aches', '', '', '', '', '', '', '', '', '', '', 10, 2, 'Legionnaires_Disease'],
        ['chest_pain', 'shortness_of_breath', 'dizziness', '', '', '', '', '', '', '', '', '', '', '', 1, 3, 'Panic_Attack'],
        ['fatigue', 'headache', 'body_aches', '', '', '', '', '', '', '', '', '', '', '', 21, 1, 'Chronic_Kidney_Disease'],
        ['nausea', 'fatigue', 'body_aches', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Thyroid_Disorder'],
        ['fever', 'fatigue', 'body_aches', 'headache', '', '', '', '', '', '', '', '', '', '', 5, 2, 'Lyme_Disease'],
        ['cough', 'fever', 'fatigue', '', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Pneumocystis_Pneumonia'],
        ['headache', 'nausea', 'fever', '', '', '', '', '', '', '', '', '', '', '', 3, 2, 'Encephalitis'],
        ['diarrhea', 'nausea', 'fever', 'fatigue', '', '', '', '', '', '', '', '', '', '', 5, 2, 'Cholera'],
        ['fever', 'headache', 'body_aches', '', '', '', '', '', '', '', '', '', '', '', 7, 2, 'Dengue_Fever'],
        ['cough', 'fever', 'chest_pain', 'fatigue', '', '', '', '', '', '', '', '', '', '', 21, 2, 'Histoplasmosis'],
        ['fatigue', 'fever', 'body_aches', 'headache', '', '', '', '', '', '', '', '', '', '', 14, 2, 'Epstein_Barr_Virus']
    ]
    
    # Generate additional samples through variations
    extended_data = []
    
    # Add base samples
    for sample in data:
        extended_data.append(sample)
    
    # Generate variations for more training data
    import random
    
    for _ in range(985 - len(data)):  # Generate to reach 985 total samples
        base_sample = random.choice(data)
        varied_sample = base_sample.copy()
        
        # Add minor variations
        # Vary duration slightly
        varied_sample[14] = max(1, varied_sample[14] + random.randint(-2, 2))
        
        # Vary intensity slightly  
        varied_sample[15] = max(1, min(3, varied_sample[15] + random.randint(-1, 1)))
        
        # Sometimes add/remove a symptom
        if random.random() < 0.3:  # 30% chance
            symptom_positions = [i for i in range(14) if varied_sample[i] == '']
            if symptom_positions:
                pos = random.choice(symptom_positions)
                # Add a related symptom
                related_symptoms = ['fatigue', 'headache', 'body_aches', 'dizziness']
                varied_sample[pos] = random.choice(related_symptoms)
        
        extended_data.append(varied_sample)
    
    return extended_data

def prepare_features_and_labels(data):
    """Prepare feature vectors and labels from raw data"""
    
    # Define feature columns
    symptom_features = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache',
        'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose',
        'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
    ]
    
    features = []
    labels = []
    
    for sample in data:
        # Create feature vector
        feature_vector = []
        
        # Symptom features (binary)
        for i, symptom in enumerate(symptom_features):
            if symptom in sample[:14]:  # First 14 positions are symptoms
                feature_vector.append(1.0)
            else:
                feature_vector.append(0.0)
        
        # Duration (numeric)
        feature_vector.append(float(sample[14]))  # Position 14 for duration
        
        # Intensity (numeric)  
        feature_vector.append(float(sample[15]))  # Position 15 for intensity
        
        features.append(feature_vector)
        labels.append(sample[16])  # Diagnosis is at position 16
    
    return np.array(features), np.array(labels), symptom_features + ['duration_days', 'intensity']

def train_comprehensive_model():
    """Train the comprehensive AI diagnosis model"""
    
    print("🤖 Training Comprehensive AI Diagnosis Model")
    print("="*60)
    
    # Load training data
    print("📊 Loading training data...")
    raw_data = load_training_data()
    print(f"✅ Loaded {len(raw_data)} training samples")
    
    # Prepare features and labels
    print("🔧 Preparing features and labels...")
    X, y, feature_names = prepare_features_and_labels(raw_data)
    print(f"✅ Features shape: {X.shape}")
    print(f"✅ Unique diagnoses: {len(np.unique(y))}")
    
    # Encode labels
    print("🏷️ Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    print("🔀 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Train model
    print("🎯 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    print("📈 Evaluating model...")
    train_accuracy = accuracy_score(y_train, model.predict(X_train))
    test_accuracy = accuracy_score(y_test, model.predict(X_test))
    
    print(f"✅ Training Accuracy: {train_accuracy:.3f}")
    print(f"✅ Testing Accuracy: {test_accuracy:.3f}")
    
    # Save model components
    print("💾 Saving model components...")
    
    with open('final_comprehensive_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('final_comprehensive_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    with open('final_comprehensive_features.pkl', 'wb') as f:
        pickle.dump(feature_names, f)
    
    print("✅ Model saved successfully!")
    
    # Generate detailed report
    print("\n📋 Generating Classification Report...")
    y_pred = model.predict(X_test)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                              target_names=label_encoder.classes_,
                              zero_division=0))
    
    # Feature importance
    print("\n🎯 Top 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10))
    
    # Save feature importance plot
    plt.figure(figsize=(10, 6))
    top_features = feature_importance.head(10)
    plt.barh(top_features['feature'], top_features['importance'])
    plt.title('Top 10 Feature Importance')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Confusion matrix for top diagnoses
    if len(label_encoder.classes_) <= 20:  # Only if manageable size
        plt.figure(figsize=(12, 10))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=label_encoder.classes_,
                   yticklabels=label_encoder.classes_)
        plt.title('Confusion Matrix')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # Training summary
    training_summary = {
        'timestamp': datetime.now().isoformat(),
        'samples': len(raw_data),
        'features': len(feature_names),
        'diagnoses': len(label_encoder.classes_),
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'model_params': model.get_params()
    }
    
    with open('training_summary.json', 'w') as f:
        import json
        json.dump(training_summary, f, indent=2)
    
    print(f"\n🎉 Training completed successfully!")
    print(f"📊 Final model supports {len(label_encoder.classes_)} diagnoses")
    print(f"📈 Test accuracy: {test_accuracy:.3f}")
    
    return model, label_encoder, feature_names

def test_trained_model():
    """Test the trained model with sample cases"""
    
    print("\n🧪 Testing Trained Model")
    print("="*40)
    
    try:
        # Load model components
        with open('final_comprehensive_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('final_comprehensive_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        with open('final_comprehensive_features.pkl', 'rb') as f:
            feature_names = pickle.load(f)
        
        # Test cases
        test_cases = [
            {
                'name': 'Flu-like symptoms',
                'features': [1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 5, 2]  # fever, cough, fatigue, headache, sore_throat, body_aches, 5 days, moderate
            },
            {
                'name': 'COVID-like symptoms', 
                'features': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 10, 2]  # fever, cough, fatigue, shortness_of_breath, loss_of_taste, loss_of_smell, 10 days, moderate
            },
            {
                'name': 'Migraine symptoms',
                'features': [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 3]  # fatigue, headache, nausea, dizziness, 1 day, severe
            }
        ]
        
        for case in test_cases:
            print(f"\n--- {case['name']} ---")
            
            # Make prediction
            prediction = model.predict([case['features']])[0]
            probabilities = model.predict_proba([case['features']])[0]
            confidence = probabilities[prediction]
            
            # Get diagnosis name
            diagnosis = label_encoder.inverse_transform([prediction])[0]
            
            print(f"Predicted: {diagnosis}")
            print(f"Confidence: {confidence:.3f}")
            
            # Show top 3 predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            print("Top 3 predictions:")
            for i, idx in enumerate(top_indices):
                diag = label_encoder.inverse_transform([idx])[0]
                conf = probabilities[idx]
                print(f"  {i+1}. {diag}: {conf:.3f}")
        
        print("\n✅ Model testing completed!")
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")

if __name__ == "__main__":
    # Train the model
    model, encoder, features = train_comprehensive_model()
    
    # Test the model
    test_trained_model()
