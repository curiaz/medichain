"""
Production startup script for MediChain with notification system
"""

# Temporarily disable debug mode to prevent restart issues
import os
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import and run the main app
from app import app

if __name__ == '__main__':
    print("🚀 Starting MediChain Backend with Notification System (Production Mode)")
    print("📊 Supabase will run in fallback mode if SSL issues occur")
    print("🔔 Notification system fully integrated")
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False,  # Disable debug to prevent restart loops
        threaded=True
    )