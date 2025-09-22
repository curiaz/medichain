#!/usr/bin/env bash
# MediChain Test Runner
# Runs both backend and frontend tests

echo "🚀 Running MediChain Test Suite"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

BACKEND_PASSED=true
FRONTEND_PASSED=true

# Backend Tests
echo ""
echo "🧪 Running Backend Tests..."
echo "---------------------------"

cd backend

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    BACKEND_PASSED=false
else
    # Install dependencies if needed
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing backend dependencies..."
        pip install -r requirements.txt > /dev/null 2>&1
    fi

    # Run tests
    if python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing > ../backend_test_results.txt 2>&1; then
        print_status "Backend tests passed"
    else
        print_error "Backend tests failed"
        BACKEND_PASSED=false
        echo "Check backend_test_results.txt for details"
    fi
fi

cd ..

# Frontend Tests
echo ""
echo "🧪 Running Frontend Tests..."
echo "----------------------------"

# Check if Node.js is available
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed or not in PATH"
    FRONTEND_PASSED=false
else
    # Install dependencies if needed
    if [ -f "package.json" ]; then
        echo "📦 Installing frontend dependencies..."
        npm ci > /dev/null 2>&1
    fi

    # Run tests
    if npm run test:ci > frontend_test_results.txt 2>&1; then
        print_status "Frontend tests passed"
    else
        print_error "Frontend tests failed"
        FRONTEND_PASSED=false
        echo "Check frontend_test_results.txt for details"
    fi
fi

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="

if [ "$BACKEND_PASSED" = true ]; then
    print_status "Backend: PASSED"
else
    print_error "Backend: FAILED"
fi

if [ "$FRONTEND_PASSED" = true ]; then
    print_status "Frontend: PASSED"
else
    print_error "Frontend: FAILED"
fi

echo ""
if [ "$BACKEND_PASSED" = true ] && [ "$FRONTEND_PASSED" = true ]; then
    print_status "All tests passed! 🎉"
    exit 0
else
    print_error "Some tests failed. Please check the log files for details."
    exit 1
fi
