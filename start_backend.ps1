# MediChain Patient Profile Backend Integration Startup Script (PowerShell)

Write-Host "🏥 MediChain Patient Profile Management - Backend Integration" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: Please run this script from the medichain root directory" -ForegroundColor Red
    exit 1
}

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Backend directory not found" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Starting backend integration process..." -ForegroundColor Yellow

# Step 1: Check Python installation
Write-Host ""
Write-Host "1️⃣ Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Check if virtual environment exists
Write-Host ""
Write-Host "2️⃣ Checking Python virtual environment..." -ForegroundColor Green
if (-not (Test-Path "backend\venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating one..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    Set-Location ..
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
}

# Step 3: Activate virtual environment and install dependencies
Write-Host ""
Write-Host "3️⃣ Installing Python dependencies..." -ForegroundColor Green
Set-Location backend
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 4: Check environment file
Write-Host ""
Write-Host "4️⃣ Checking environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating template..." -ForegroundColor Yellow
    @"
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Flask Configuration
SECRET_KEY=your_flask_secret_key
FLASK_DEBUG=True
FLASK_ENV=development
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "📝 Please update the .env file with your Supabase credentials" -ForegroundColor Yellow
    Write-Host "   You can find these in your Supabase project settings" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Step 5: Test database connection
Write-Host ""
Write-Host "5️⃣ Testing database connection..." -ForegroundColor Green
try {
    python -c "from db.supabase_client import SupabaseClient; client = SupabaseClient(); print('✅ Database connection successful')"
    if ($LASTEXITCODE -ne 0) {
        throw "Database connection failed"
    }
} catch {
    Write-Host "❌ Database connection failed" -ForegroundColor Red
    Write-Host "💡 Please check your Supabase credentials in .env file" -ForegroundColor Yellow
}

# Step 6: Start the Flask server
Write-Host ""
Write-Host "6️⃣ Starting Flask development server..." -ForegroundColor Green
Write-Host "🚀 Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📋 API endpoints:" -ForegroundColor Cyan
Write-Host "   GET    /api/profile/patient" -ForegroundColor White
Write-Host "   PUT    /api/profile/patient" -ForegroundColor White
Write-Host "   PUT    /api/profile/patient/medical" -ForegroundColor White
Write-Host "   POST   /api/profile/patient/documents" -ForegroundColor White
Write-Host "   PUT    /api/profile/patient/privacy" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask server
python app.py

