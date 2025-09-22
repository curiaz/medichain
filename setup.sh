#!/bin/bash

# MediChain Firebase + Supabase Setup Script
echo "🏥 MediChain Firebase + Supabase Setup"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory (where package.json is located)"
    exit 1
fi

print_status "Starting MediChain setup..."

# 1. Install Frontend Dependencies
print_status "Installing frontend dependencies..."
if command -v npm >/dev/null 2>&1; then
    npm install firebase @supabase/supabase-js
    if [ $? -eq 0 ]; then
        print_success "Frontend dependencies installed successfully"
    else
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
else
    print_error "npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# 2. Install Backend Dependencies
print_status "Installing backend Python dependencies..."
cd backend

if command -v pip >/dev/null 2>&1; then
    pip install firebase-admin supabase python-dotenv
    if [ $? -eq 0 ]; then
        print_success "Backend dependencies installed successfully"
    else
        print_error "Failed to install backend dependencies"
        exit 1
    fi
else
    print_error "pip is not installed. Please install Python and pip first."
    exit 1
fi

cd ..

# 3. Create environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please update .env file with your actual Firebase and Supabase credentials"
    else
        print_error ".env.example file not found"
    fi
else
    print_warning ".env file already exists. Please verify your configuration."
fi

# 4. Check directory structure
print_status "Checking project structure..."

directories=(
    "src/config"
    "src/context"
    "backend/auth"
    "backend/db"
    "database"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory $dir exists"
    else
        print_warning "Directory $dir not found, creating..."
        mkdir -p "$dir"
    fi
done

# 5. Summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
print_status "Next steps:"
echo "1. Update your .env file with Firebase and Supabase credentials"
echo "2. Run the database schema in your Supabase dashboard"
echo "3. Start the frontend: npm start"
echo "4. Start the backend: cd backend && python app.py"
echo ""
print_status "Configuration files created:"
echo "- src/config/firebase.js (Firebase configuration)"
echo "- src/config/supabase.js (Supabase configuration)"
echo "- src/context/FirebaseAuthContext.jsx (Authentication context)"
echo "- backend/auth/firebase_auth.py (Firebase backend service)"
echo "- backend/auth/firebase_auth_routes.py (Authentication routes)"
echo "- database/enhanced_schema.sql (Database schema)"
echo ""
print_success "MediChain is ready for configuration! 🚀"
