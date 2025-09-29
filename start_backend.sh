#!/bin/bash
# MediChain Patient Profile Backend Integration Startup Script

echo "🏥 MediChain Patient Profile Management - Backend Integration"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the medichain root directory"
    exit 1
fi

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: Backend directory not found"
    exit 1
fi

echo "📋 Starting backend integration process..."

# Step 1: Check Python installation
echo ""
echo "1️⃣ Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is installed"
    python3 --version
else
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Step 2: Check if virtual environment exists
echo ""
echo "2️⃣ Checking Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Step 3: Activate virtual environment and install dependencies
echo ""
echo "3️⃣ Installing Python dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 4: Check environment file
echo ""
echo "4️⃣ Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Flask Configuration
SECRET_KEY=your_flask_secret_key
FLASK_DEBUG=True
FLASK_ENV=development
EOF
    echo "📝 Please update the .env file with your Supabase credentials"
    echo "   You can find these in your Supabase project settings"
else
    echo "✅ .env file exists"
fi

# Step 5: Test database connection
echo ""
echo "5️⃣ Testing database connection..."
python -c "
from db.supabase_client import SupabaseClient
try:
    client = SupabaseClient()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('💡 Please check your Supabase credentials in .env file')
"

# Step 6: Start the Flask server
echo ""
echo "6️⃣ Starting Flask development server..."
echo "🚀 Server will be available at: http://localhost:5000"
echo "📋 API endpoints:"
echo "   GET    /api/profile/patient"
echo "   PUT    /api/profile/patient"
echo "   PUT    /api/profile/patient/medical"
echo "   POST   /api/profile/patient/documents"
echo "   PUT    /api/profile/patient/privacy"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask server
python app.py

