"""
MediChain Backend Application
Integrates Firebase Authentication and Supabase Storage
"""
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import our services
from auth.firebase_auth_routes import auth_firebase_bp
from medical_routes import medical_bp
from appointment_routes import appointments_bp
from db.supabase_client import SupabaseClient

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Register blueprints
app.register_blueprint(auth_firebase_bp)
app.register_blueprint(medical_bp)
app.register_blueprint(appointments_bp)

# Initialize Supabase client
supabase = SupabaseClient()

@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'status': 'MediChain Backend is running!',
        'version': '1.0.0',
        'services': {
            'firebase_auth': 'configured',
            'supabase_storage': 'configured',
            'medical_records': 'available',
            'appointments': 'available'
        },
        'endpoints': {
            'auth': '/api/auth/*',
            'medical': '/api/medical/*',
            'appointments': '/api/appointments/*'
        }
    }

@app.route('/api/health')
def health_check():
    """Detailed health check"""
    try:
        # Test Supabase connection
        supabase_status = 'connected' if supabase.client else 'disconnected'

        return {
            'status': 'healthy',
            'services': {
                'supabase': supabase_status,
                'firebase': 'configured'  # Firebase is initialized in the auth service
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
