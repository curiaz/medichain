import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def train_diagnosis_model():
    """Train the AI diagnosis model"""
    
    # Load dataset
    print("Loading dataset...")
    try:
        df = pd.read_csv('symptoms_dataset_balanced.csv')
        print("Using balanced dataset")
    except FileNotFoundError:
        try:
            df = pd.read_csv('symptoms_dataset_expanded.csv')
            print("Using expanded dataset")
        except FileNotFoundError:
            df = pd.read_csv('symptoms_dataset.csv')
            print("Using original dataset")
    
    # Drop classes with fewer than 2 samples (fix for stratify issue)
    class_counts = df['diagnosis'].value_counts()
    print(f"Total classes in dataset: {len(class_counts)}")
    print(f"Class distribution:\n{class_counts}")
    
    # Keep only classes with at least 2 samples for stratified splitting
    valid_classes = class_counts[class_counts >= 2].index
    df = df[df['diagnosis'].isin(valid_classes)]
    
    if df.empty:
        raise ValueError("Dataset has no valid classes with at least 2 samples.")
    
    print(f"After filtering, using {len(valid_classes)} classes with {len(df)} samples")
    
    # Separate features and target
    X = df.drop('diagnosis', axis=1)
    y = df['diagnosis']
    
    # Store feature names
    feature_names = X.columns.tolist()
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Check if we have enough samples for stratified split
    min_class_count = min(pd.Series(y_encoded).value_counts())
    num_classes = len(np.unique(y_encoded))
    test_size = 0.2
    
    # Calculate minimum samples needed for stratified split
    min_test_samples_needed = num_classes
    current_test_samples = int(len(df) * test_size)
    
    print(f"Number of classes: {num_classes}")
    print(f"Total samples: {len(df)}")
    print(f"Proposed test samples: {current_test_samples}")
    print(f"Minimum test samples needed for stratified split: {min_test_samples_needed}")
    
    # Adjust strategy based on data constraints
    if current_test_samples < min_test_samples_needed:
        print("Not enough samples for stratified split. Using simple random split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42
        )
    else:
        # Try stratified split with adjusted test size if needed
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )
            print("Using stratified split")
        except ValueError as e:
            print(f"Stratified split failed: {e}")
            print("Falling back to simple random split")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42
            )
    
    # Train model
    print("Training model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    
    # Get the classes that are actually present in the test set
    unique_test_classes = np.unique(y_test)
    test_class_names = [label_encoder.classes_[i] for i in unique_test_classes]
    
    print(classification_report(y_test, y_pred, 
                              labels=unique_test_classes,
                              target_names=test_class_names,
                              zero_division=0))
    
    # Create confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=unique_test_classes)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=test_class_names,
                yticklabels=test_class_names)
    plt.title('Confusion Matrix - Diagnosis Model')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feature_importance, x='importance', y='feature')
    plt.title('Feature Importance - Diagnosis Model')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save model and encoders
    print("Saving model...")
    joblib.dump(model, 'diagnosis_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    joblib.dump(feature_names, 'feature_names.pkl')
    
    print("Model training completed!")
    print(f"Model saved as: diagnosis_model.pkl")
    print(f"Label encoder saved as: label_encoder.pkl")
    print(f"Feature names saved as: feature_names.pkl")
    
    return model, label_encoder, feature_names

if __name__ == "__main__":
    train_diagnosis_model()
