# AI Diagnosis System for MediChain

This directory contains the AI-powered diagnosis system for the MediChain healthcare platform.

## Overview

The AI diagnosis system uses machine learning to predict medical conditions based on patient symptoms. It includes:
- A trained Random Forest classifier for diagnosis prediction
- REST API endpoints for symptom analysis
- Comprehensive testing utilities

## Files

- `train_diagnosis_model.py` - Script to train the diagnosis prediction model
- `run_ai_server.py` - Flask server providing AI diagnosis API endpoints
- `test_ai_diagnosis.py` - Testing script for the AI diagnosis API
- `requirements_ai.txt` - Python dependencies for the AI system
- `symptoms_dataset.csv` - Training dataset (symptoms and diagnoses)
- `AI_Diagnosis_Model_Training.ipynb` - Jupyter notebook for model development

## Setup Instructions

### 1. Install Dependencies

```bash
cd medichain/backend
pip install -r requirements_ai.txt
```

### 2. Train the Model

```bash
python train_diagnosis_model.py
```

This will:
- Load the symptoms dataset
- Train a Random Forest classifier
- Save the model, label encoder, and feature names as pickle files

### 3. Start the AI Server

```bash
python run_ai_server.py
```

The server will start on `http://localhost:5001`

### 4. Test the System

In a new terminal:
```bash
python test_ai_diagnosis.py
```

## API Endpoints

### Health Check
- **GET** `/health` - Check if the model is loaded and server is healthy

### Symptoms
- **GET** `/symptoms` - Get list of available symptoms

### Diagnoses
- **GET** `/diagnoses` - Get list of available diagnoses

### Prediction
- **POST** `/predict` - Predict diagnosis from symptoms
  ```json
  {
    "symptoms": {
      "fever": 1,
      "cough": 1,
      "fatigue": 0,
      "shortness_of_breath": 0,
      "headache": 1,
      "sore_throat": 0
    }
  }
  ```

### Batch Prediction
- **POST** `/predict/batch` - Predict diagnoses for multiple cases
  ```json
  {
    "cases": [
      {
        "id": "case1",
        "symptoms": {...}
      },
      {
        "id": "case2",
        "symptoms": {...}
      }
    ]
  }
  ```

## Example Usage

### Single Prediction
```python
import requests

response = requests.post('http://localhost:5001/predict', json={
    'symptoms': {
        'fever': 1,
        'cough': 1,
        'fatigue': 1,
        'shortness_of_breath': 0,
        'headache': 1,
        'sore_throat': 1
    }
})

result = response.json()
print(f"Predicted diagnosis: {result['diagnosis']}")
print(f"Confidence: {result['confidence']}")
```

## Model Performance

The current model achieves:
- **Accuracy**: ~95% on test data
- **Precision**: High for common diagnoses
- **Recall**: Good across all diagnosis categories

## Integration with MediChain

The AI diagnosis system can be integrated with the main MediChain platform by:
1. Starting the AI server on port 5001
2. Updating the frontend to call the AI endpoints
3. Storing predictions in the blockchain for auditability

## Troubleshooting

### Model Not Found
If you get "Model file not found" errors:
1. Ensure you've run `python train_diagnosis_model.py`
2. Check that `diagnosis_model.pkl` exists in the backend directory

### Port Already in Use
If port 5001 is already in use:
```bash
python run_ai_server.py --port 5002
```

### Dependencies Issues
If you encounter dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements_ai.txt --force-reinstall
```

## Development

To improve the model:
1. Add more training data to `symptoms_dataset.csv`
2. Experiment with different algorithms in `AI_Diagnosis_Model_Training.ipynb`
3. Retrain the model with `python train_diagnosis_model.py`
4. Test with `python test_ai_diagnosis.py`
