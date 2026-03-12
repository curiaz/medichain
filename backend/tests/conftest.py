"""
Pytest configuration and fixtures for backend tests
"""
import os
import sys
import pytest
from unittest.mock import Mock, MagicMock

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set environment variables for testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'
os.environ['FIREBASE_PROJECT_ID'] = 'test-project'
os.environ['FIREBASE_PRIVATE_KEY'] = 'test-private-key'
os.environ['FIREBASE_CLIENT_EMAIL'] = 'test@test.com'


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    mock = MagicMock()
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.delete.return_value = mock
    mock.eq.return_value = mock
    mock.single.return_value = mock
    mock.execute.return_value = Mock(data=None, error=None)
    return mock


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase auth for testing"""
    mock = MagicMock()
    mock.get_user.return_value = Mock(uid='test-uid', email='test@test.com')
    mock.delete_user.return_value = None
    mock.update_user.return_value = None
    mock.get_user_by_email.return_value = Mock(uid='test-uid', email='test@test.com')
    return mock


@pytest.fixture
def mock_flask_app():
    """Mock Flask app for testing"""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(mock_flask_app):
    """Test client fixture"""
    return mock_flask_app.test_client()


# Configure pytest to ignore warnings
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
