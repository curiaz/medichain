#!/usr/bin/env python3
"""
Enhanced Model Training Script for MediChain Comprehensive AI
Trains the model with all new columns including diagnosis descriptions and recommended actions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import json
from datetime import datetime

def train_enhanced_model():
    """Train the ML model with the new enhanced dataset including descriptions and actions"""
    
    print("🚀 Training Enhanced MediChain AI Model...")
    print("=" * 60)
    
    # Load the enhanced dataset
    dataset_path = 'final_enhanced_dataset.csv'
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return False
    
    print(f"📊 Loading enhanced dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Total records: {len(df)}")
    print(f"Unique diagnoses: {df['diagnosis'].nunique()}")
    
    # Display new columns
    new_columns = ['diagnosis_description', 'recommended_action', 'duration_days', 
                   'intensity', 'complications_risk', 'hospital_visit_required']
    print(f"New enhanced features: {[col for col in new_columns if col in df.columns]}")
    
    # Define all symptom columns (binary features)
    symptom_columns = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache',
        'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose',
        'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
    ]
    
    # Define categorical features
    categorical_columns = [
        'age_group', 'gender', 'underlying_conditions', 'recent_exposure', 
        'symptom_onset', 'progression', 'treatment_received'
    ]
    
    # Define numerical features  
    numerical_columns = [
        'duration_days', 'intensity', 'recovery_time_days'
    ]
    
    # Define boolean features
    boolean_columns = [
        'hospital_visit_required'
    ]
    
    # Define risk level features
    risk_columns = [
        'complications_risk'
    ]
    
    # All feature columns
    all_feature_columns = (symptom_columns + categorical_columns + 
                          numerical_columns + boolean_columns + risk_columns)
    
    # Check which columns exist in the dataset
    available_features = [col for col in all_feature_columns if col in df.columns]
    missing_features = [col for col in all_feature_columns if col not in df.columns]
    
    print(f"✅ Available features ({len(available_features)}): {available_features}")
    if missing_features:
        print(f"⚠️  Missing features: {missing_features}")
    
    # Prepare feature encoders
    encoders = {}
    
    # Encode categorical features
    for col in categorical_columns:
        if col in df.columns:
            encoder = LabelEncoder()
            df[f'{col}_encoded'] = encoder.fit_transform(df[col].astype(str))
            encoders[col] = encoder
            print(f"🔢 Encoded {col}: {len(encoder.classes_)} categories")
    
    # Encode boolean features
    for col in boolean_columns:
        if col in df.columns:
            df[f'{col}_encoded'] = df[col].astype(str).map({'yes': 1, 'True': 1, 'true': 1, 'no': 0, 'False': 0, 'false': 0}).fillna(0)
    
    # Encode risk levels
    for col in risk_columns:
        if col in df.columns:
            risk_mapping = {'low': 0, 'medium': 1, 'high': 2}
            df[f'{col}_encoded'] = df[col].astype(str).map(risk_mapping).fillna(1)
    
    # Create final feature set
    final_features = []
    
    # Add symptom columns
    for col in symptom_columns:
        if col in df.columns:
            final_features.append(col)
    
    # Add encoded categorical columns
    for col in categorical_columns:
        if col in df.columns:
            final_features.append(f'{col}_encoded')
    
    # Add numerical columns
    for col in numerical_columns:
        if col in df.columns:
            # Fill missing values with median
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median())
            final_features.append(col)
    
    # Add encoded boolean columns
    for col in boolean_columns:
        if col in df.columns:
            final_features.append(f'{col}_encoded')
            
    # Add encoded risk columns
    for col in risk_columns:
        if col in df.columns:
            final_features.append(f'{col}_encoded')
    
    print(f"🎯 Final feature set ({len(final_features)}): {final_features}")
    
    # Prepare training data
    X = df[final_features].copy()
    
    # Fill any remaining missing values
    X = X.fillna(0)
    
    # Encode target diagnosis
    diagnosis_encoder = LabelEncoder()
    y = diagnosis_encoder.fit_transform(df['diagnosis'])
    
    print(f"🎯 Target diagnoses: {len(diagnosis_encoder.classes_)} unique conditions")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 Training set: {X_train.shape[0]} samples")
    print(f"📊 Test set: {X_test.shape[0]} samples")
    
    # Train the enhanced model
    print("🧠 Training Enhanced Random Forest Model...")
    model = RandomForestClassifier(
        n_estimators=200,  # More trees for better performance
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"🎯 Model Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': final_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔝 Top 10 Most Important Features:")
    for _, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")
    
    # Create diagnosis information mapping
    diagnosis_info = {}
    for _, row in df.iterrows():
        diagnosis = row['diagnosis']
        if diagnosis not in diagnosis_info:
            diagnosis_info[diagnosis] = {
                'description': row.get('diagnosis_description', 'Medical condition requiring professional evaluation.'),
                'recommended_action': row.get('recommended_action', 'Consult a healthcare provider for proper evaluation and treatment.'),
                'typical_duration': row.get('duration_days', 'Variable'),
                'severity_indicators': {
                    'low': 'mild symptoms, manageable at home',
                    'moderate': 'noticeable symptoms, may need medical attention',
                    'severe': 'significant symptoms, seek immediate care'
                }
            }
    
    # Save all model components
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save the trained model
    model_path = 'final_comprehensive_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"💾 Model saved: {model_path}")
    
    # Save the diagnosis encoder
    encoder_path = 'final_comprehensive_encoder.pkl'
    with open(encoder_path, 'wb') as f:
        pickle.dump(diagnosis_encoder, f)
    print(f"💾 Diagnosis encoder saved: {encoder_path}")
    
    # Save feature information
    features_path = 'final_comprehensive_features.pkl'
    feature_info = {
        'features': final_features,
        'symptom_columns': symptom_columns,
        'categorical_encoders': encoders,
        'feature_importance': feature_importance.to_dict('records')
    }
    with open(features_path, 'wb') as f:
        pickle.dump(feature_info, f)
    print(f"💾 Feature info saved: {features_path}")
    
    # Save diagnosis information
    diagnosis_info_path = 'diagnosis_information.json'
    with open(diagnosis_info_path, 'w') as f:
        json.dump(diagnosis_info, f, indent=2)
    print(f"💾 Diagnosis info saved: {diagnosis_info_path}")
    
    # Save training summary
    training_summary = {
        'timestamp': timestamp,
        'dataset_size': len(df),
        'num_features': len(final_features),
        'num_diagnoses': len(diagnosis_encoder.classes_),
        'accuracy': float(accuracy),
        'model_type': 'RandomForestClassifier',
        'feature_columns': final_features,
        'new_enhancements': [
            'diagnosis_description',
            'recommended_action', 
            'enhanced_feature_encoding',
            'improved_categorical_handling',
            'risk_level_integration'
        ]
    }
    
    summary_path = 'training_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(training_summary, f, indent=2)
    print(f"💾 Training summary saved: {summary_path}")
    
    print("\n🎉 Enhanced Model Training Complete!")
    print(f"✅ Accuracy: {accuracy*100:.1f}%")
    print(f"✅ Features: {len(final_features)}")
    print(f"✅ Diagnoses: {len(diagnosis_encoder.classes_)}")
    print(f"✅ Enhanced with descriptions and recommendations")
    
    return True

if __name__ == "__main__":
    success = train_enhanced_model()
    if success:
        print("🚀 Enhanced model ready for deployment!")
    else:
        print("❌ Training failed!")