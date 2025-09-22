# MediChain Firebase + Supabase Setup Script for Windows
Write-Host "🏥 MediChain Firebase + Supabase Setup" -ForegroundColor Cyan
Write-Host "====================================="

function Print-Status($message) {
    Write-Host "[INFO] $message" -ForegroundColor Blue
}

function Print-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Print-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Print-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Print-Error "Please run this script from the project root directory (where package.json is located)"
    exit 1
}

Print-Status "Starting MediChain setup..."

# 1. Install Frontend Dependencies
Print-Status "Installing frontend dependencies..."
try {
    npm install firebase @supabase/supabase-js
    Print-Success "Frontend dependencies installed successfully"
}
catch {
    Print-Error "Failed to install frontend dependencies. Make sure npm is installed."
    exit 1
}

# 2. Install Backend Dependencies
Print-Status "Installing backend Python dependencies..."
Set-Location backend

try {
    pip install firebase-admin supabase python-dotenv
    Print-Success "Backend dependencies installed successfully"
}
catch {
    Print-Error "Failed to install backend dependencies. Make sure Python and pip are installed."
    exit 1
}

Set-Location ..

# 3. Create environment file
Print-Status "Setting up environment configuration..."
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Print-Success "Created .env file from template"
        Print-Warning "Please update .env file with your actual Firebase and Supabase credentials"
    }
    else {
        Print-Error ".env.example file not found"
    }
}
else {
    Print-Warning ".env file already exists. Please verify your configuration."
}

# 4. Check directory structure
Print-Status "Checking project structure..."

$directories = @(
    "src\config",
    "src\context",
    "backend\auth",
    "backend\db",
    "database"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Print-Success "Directory $dir exists"
    }
    else {
        Print-Warning "Directory $dir not found, creating..."
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# 5. Summary
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Cyan
Write-Host "=================="
Write-Host ""
Print-Status "Next steps:"
Write-Host "1. Update your .env file with Firebase and Supabase credentials"
Write-Host "2. Run the database schema in your Supabase dashboard"
Write-Host "3. Start the frontend: npm start"
Write-Host "4. Start the backend: cd backend && python app.py"
Write-Host ""
Print-Status "Configuration files created:"
Write-Host "- src/config/firebase.js (Firebase configuration)"
Write-Host "- src/config/supabase.js (Supabase configuration)"
Write-Host "- src/context/FirebaseAuthContext.jsx (Authentication context)"
Write-Host "- backend/auth/firebase_auth.py (Firebase backend service)"
Write-Host "- backend/auth/firebase_auth_routes.py (Authentication routes)"
Write-Host "- database/enhanced_schema.sql (Database schema)"
Write-Host ""
Print-Success "MediChain is ready for configuration! 🚀"
