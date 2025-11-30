"""
Unit tests for main Flask app (app.py)
Tests the AI diagnosis system, routes, and health endpoints
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


class TestAppRoutes:
    """Test cases for main app routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked app"""
        # Mock the StreamlinedAIDiagnosis initialization
        with patch('app.StreamlinedAIDiagnosis') as mock_ai_class:
            mock_ai_instance = MagicMock()
            mock_ai_instance.model_version = "test-version"
            mock_ai_instance.conditions_df = MagicMock()
            mock_ai_instance.symptom_columns = ['fever', 'cough', 'headache']
            mock_ai_class.return_value = mock_ai_instance
            
            # Import app after mocking
            from app import app as flask_app
            flask_app.config['TESTING'] = True
            
            with flask_app.test_client() as client:
                yield client
    
    def test_home_route(self, client):
        """Test home route returns API info"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'MediChain API v5.0 - Streamlined'
        assert data['status'] == 'active'
        assert 'endpoints' in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    @patch('app.ai_engine')
    def test_ai_health_available(self, mock_ai_engine, client):
        """Test AI health endpoint when AI is available"""
        mock_ai_engine.model_version = "test-version"
        mock_ai_engine.conditions_df = MagicMock()
        type(mock_ai_engine.conditions_df).__len__ = Mock(return_value=100)
        mock_ai_engine.symptom_columns = ['fever', 'cough']
        
        response = client.get('/api/ai/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['ai_system'] == 'test-version'
    
    @patch('app.ai_engine', None)
    def test_ai_health_unavailable(self, client):
        """Test AI health endpoint when AI is unavailable"""
        response = client.get('/api/ai/health')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not initialized' in data['message'].lower()
    
    @patch('app.ai_engine')
    def test_get_symptoms_success(self, mock_ai_engine, client):
        """Test getting symptoms list"""
        mock_ai_engine.symptom_columns = ['fever', 'dry_cough', 'sore_throat']
        
        response = client.get('/api/symptoms')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'symptoms' in data
        assert len(data['symptoms']) == 3
        assert data['count'] == 3
    
    @patch('app.ai_engine', None)
    def test_get_symptoms_unavailable(self, client):
        """Test getting symptoms when AI engine is unavailable"""
        response = client.get('/api/symptoms')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('app.ai_engine')
    def test_diagnose_success(self, mock_ai_engine, client):
        """Test diagnosis endpoint with valid symptoms"""
        mock_ai_engine.diagnose.return_value = {
            'success': True,
            'message': 'Diagnosis completed successfully',
            'data': {
                'detected_symptoms': ['Fever', 'Cough'],
                'primary_condition': 'Common Cold',
                'primary_confidence': '85.5%',
                'detailed_results': []
            }
        }
        
        response = client.post('/api/diagnose',
                              data=json.dumps({'symptoms': 'I have fever and cough'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    @patch('app.ai_engine', None)
    def test_diagnose_unavailable(self, client):
        """Test diagnosis when AI engine is unavailable"""
        response = client.post('/api/diagnose',
                              data=json.dumps({'symptoms': 'I have fever'}),
                              content_type='application/json')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('app.ai_engine')
    def test_diagnose_missing_symptoms(self, mock_ai_engine, client):
        """Test diagnosis with missing symptoms"""
        response = client.post('/api/diagnose',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'symptoms' in data['message'].lower()
    
    @patch('app.ai_engine')
    def test_diagnose_empty_symptoms(self, mock_ai_engine, client):
        """Test diagnosis with empty symptoms"""
        response = client.post('/api/diagnose',
                              data=json.dumps({'symptoms': '   '}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('app.ai_engine')
    def test_symptom_explanations_success(self, mock_ai_engine, client):
        """Test symptom explanations endpoint"""
        mock_ai_engine.parse_symptoms.return_value = {
            'fever': 1,
            'cough': 1,
            'headache': 0
        }
        
        response = client.post('/api/symptom-explanations',
                              data=json.dumps({'symptoms': 'fever and cough'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'detected_symptoms' in data['data']


class TestStreamlinedAIDiagnosis:
    """Test cases for StreamlinedAIDiagnosis class"""
    
    @patch('app.SupabaseClient')
    @patch('app._import_sklearn')
    def test_normalize_symptom(self, mock_sklearn, mock_supabase_class):
        """Test symptom normalization"""
        # Mock Supabase
        mock_supabase = MagicMock()
        mock_supabase.get_conditions.return_value = [{'condition': 'Cold', 'fever': 1}]
        mock_supabase.get_condition_reasons.return_value = [{'condition': 'Cold', 'reason': 'Viral'}]
        mock_supabase.get_action_conditions.return_value = [{'diagnosis': 'Cold', 'action': 'Rest'}]
        mock_supabase_class.return_value = mock_supabase
        
        # Mock sklearn
        mock_sklearn.return_value = (MagicMock(), MagicMock(), None, None, None, None)
        
        # Import and create instance
        from app import StreamlinedAIDiagnosis
        
        # Mock pandas DataFrame
        with patch('app.pd.DataFrame') as mock_df:
            mock_df_instance = MagicMock()
            mock_df_instance.columns = ['condition', 'fever', 'cough']
            mock_df_instance.__getitem__ = MagicMock(return_value=MagicMock())
            mock_df.return_value = mock_df_instance
            
            # Skip model training by patching train_model
            with patch.object(StreamlinedAIDiagnosis, 'train_model'):
                with patch.object(StreamlinedAIDiagnosis, 'load_data'):
                    ai = StreamlinedAIDiagnosis()
                    
                    # Test normalization
                    result = ai.normalize_symptom('runny nose')
                    assert result == 'runny_nose'
                    
                    result = ai.normalize_symptom('sore throat')
                    assert result == 'sore_throat'


class TestErrorHandling:
    """Test error handling in app"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with patch('app.StreamlinedAIDiagnosis') as mock_ai_class:
            mock_ai_instance = MagicMock()
            mock_ai_instance.model_version = "test-version"
            mock_ai_class.return_value = mock_ai_instance
            
            from app import app as flask_app
            flask_app.config['TESTING'] = True
            
            with flask_app.test_client() as client:
                yield client
    
    @patch('app.ai_engine')
    def test_diagnose_exception_handling(self, mock_ai_engine, client):
        """Test that exceptions in diagnose are handled gracefully"""
        mock_ai_engine.diagnose.side_effect = Exception("Test error")
        
        response = client.post('/api/diagnose',
                              data=json.dumps({'symptoms': 'fever'}),
                              content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data['message'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
