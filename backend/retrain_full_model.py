#!/usr/bin/env python3
"""
Retrain ML Model with Full Enhanced Dataset Features
This script retrains the ML model to use all 27 features from the enhanced dataset
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def retrain_full_model():
    """Retrain the ML model with all features from enhanced dataset"""
    
    print("🔄 Retraining ML Model with Full Enhanced Dataset...")
    
    # Load the enhanced dataset
    dataset_path = 'final_enhanced_dataset.csv'
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return False
    
    print(f"📊 Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Define all symptom columns (binary features)
    symptom_columns = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache',
        'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose',
        'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
    ]
    
    # Define all additional features
    additional_columns = [
        'duration_days', 'intensity', 'age_group', 'gender',
        'underlying_conditions', 'recent_exposure', 'symptom_onset',
        'progression', 'treatment_received', 'hospital_visit_required',
        'recovery_time_days', 'complications_risk'
    ]
    
    # All feature columns (27 total)
    all_feature_columns = symptom_columns + additional_columns
    
    print(f"Total features: {len(all_feature_columns)}")
    
    # Check for missing columns
    missing_cols = [col for col in all_feature_columns if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        return False
    
    # Prepare features
    print("🔧 Preparing features...")
    
    # Create feature matrix
    X = pd.DataFrame()
    
    # Add symptom columns (binary)
    for col in symptom_columns:
        X[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Add duration_days (numeric)
    X['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce').fillna(7)
    
    # Encode intensity (categorical to numeric)
    intensity_map = {'mild': 1, 'moderate': 2, 'severe': 3}
    X['intensity'] = df['intensity'].map(intensity_map).fillna(2)
    
    # Encode age_group (categorical to numeric)
    age_group_map = {'child': 1, 'teen': 2, 'adult': 3, 'senior': 4}
    X['age_group'] = df['age_group'].map(age_group_map).fillna(3)
    
    # Encode gender (categorical to numeric)
    gender_map = {'male': 1, 'female': 2, 'other': 3}
    X['gender'] = df['gender'].map(gender_map).fillna(3)
    
    # Encode underlying_conditions
    conditions_map = {'none': 0, 'diabetes': 1, 'hypertension': 2, 'heart_disease': 3, 'asthma': 4}
    X['underlying_conditions'] = df['underlying_conditions'].map(conditions_map).fillna(0)
    
    # Encode recent_exposure
    exposure_map = {'none': 0, 'sick_contact': 1, 'travel_history': 2, 'contaminated_food': 3}
    X['recent_exposure'] = df['recent_exposure'].map(exposure_map).fillna(0)
    
    # Encode symptom_onset
    onset_map = {'gradual': 1, 'sudden': 2}
    X['symptom_onset'] = df['symptom_onset'].map(onset_map).fillna(1)
    
    # Encode progression
    progression_map = {'improving': 1, 'stable': 2, 'worsening': 3}
    X['progression'] = df['progression'].map(progression_map).fillna(2)
    
    # Encode treatment_received
    treatment_map = {'none': 0, 'OTC_meds': 1, 'prescribed_meds': 2, 'hospitalization': 3}
    X['treatment_received'] = df['treatment_received'].map(treatment_map).fillna(0)
    
    # Encode hospital_visit_required (boolean)
    X['hospital_visit_required'] = df['hospital_visit_required'].map({'yes': 1, 'no': 0}).fillna(0)
    
    # Add recovery_time_days (numeric)
    X['recovery_time_days'] = pd.to_numeric(df['recovery_time_days'], errors='coerce').fillna(14)
    
    # Encode complications_risk
    risk_map = {'low': 1, 'medium': 2, 'high': 3}
    X['complications_risk'] = df['complications_risk'].map(risk_map).fillna(2)
    
    # Target variable
    y = df['diagnosis']
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target variable shape: {y.shape}")
    print(f"Feature columns: {list(X.columns)}")
    
    # Check for any NaN values
    if X.isnull().sum().sum() > 0:
        print("❌ Found NaN values in features:")
        print(X.isnull().sum()[X.isnull().sum() > 0])
        return False
    
    # Encode diagnosis labels
    print("🏷️ Encoding diagnosis labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"Number of unique diagnoses: {len(label_encoder.classes_)}")
    print(f"Sample diagnoses: {list(label_encoder.classes_)[:10]}")
    
    # Split data
    print("✂️ Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    
    # Train Random Forest model
    print("🌲 Training Random Forest model...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate model
    print("📊 Evaluating model...")
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔝 Top 10 Most Important Features:")
    print(feature_importance.head(10))
    
    # Save the retrained model components
    print("💾 Saving model components...")
    
    # Save model
    with open('final_comprehensive_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    print("✅ Model saved: final_comprehensive_model.pkl")
    
    # Save label encoder
    with open('final_comprehensive_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    print("✅ Encoder saved: final_comprehensive_encoder.pkl")
    
    # Save feature names
    with open('final_comprehensive_features.pkl', 'wb') as f:
        pickle.dump(list(X.columns), f)
    print("✅ Features saved: final_comprehensive_features.pkl")
    
    # Create feature mappings for backend
    feature_mappings = {
        'symptom_columns': symptom_columns,
        'intensity_map': intensity_map,
        'age_group_map': age_group_map,
        'gender_map': gender_map,
        'conditions_map': conditions_map,
        'exposure_map': exposure_map,
        'onset_map': onset_map,
        'progression_map': progression_map,
        'treatment_map': treatment_map,
        'risk_map': risk_map
    }
    
    with open('feature_mappings.pkl', 'wb') as f:
        pickle.dump(feature_mappings, f)
    print("✅ Feature mappings saved: feature_mappings.pkl")
    
    print("\n🎉 Model retraining completed successfully!")
    print(f"📈 Final accuracy: {accuracy:.4f}")
    print(f"🔧 Total features: 27")
    print("✨ Ready to use with enhanced AI system!")
    
    return True

if __name__ == "__main__":
    success = retrain_full_model()
    if success:
        print("\n✅ All done! The ML model is now trained with all 27 features.")
    else:
        print("\n❌ Model retraining failed. Please check the errors above.")