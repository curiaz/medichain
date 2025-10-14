#!/bin/bash

# Settings Feature Test Runner
# Comprehensive test execution script for local development

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="${1:-all}"
VERBOSE="${2:-false}"
OPEN_COVERAGE="${3:-false}"

# Functions
print_header() {
    echo ""
    echo -e "${CYAN}================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the medichain root directory"
    exit 1
fi

print_header "MediChain Settings Feature Test Suite"
print_info "Test Type: $TEST_TYPE"
print_info "Verbose: $VERBOSE"
echo ""

# Function to run frontend tests
run_frontend_tests() {
    local SETTINGS_ONLY=$1
    
    print_header "Frontend Tests"
    
    if [ "$SETTINGS_ONLY" = "true" ]; then
        print_info "Running Settings-specific frontend tests..."
        
        # SettingsPage component tests
        echo ""
        echo -e "${CYAN}Testing SettingsPage Component...${NC}"
        npm test -- src/tests/SettingsPage.test.js --coverage --watchAll=false --verbose || true
        
        # settingsService tests
        echo ""
        echo -e "${CYAN}Testing settingsService...${NC}"
        npm test -- src/tests/settingsService.test.js --coverage --watchAll=false --verbose || true
        
        # Combined coverage
        echo ""
        echo -e "${CYAN}Generating Combined Coverage Report...${NC}"
        npm test -- --testPathPattern="Settings|settings" --coverage --watchAll=false --collectCoverageFrom="src/pages/SettingsPage.jsx,src/services/settingsService.js" || true
    else
        print_info "Running all frontend tests..."
        npm test -- --coverage --watchAll=false || true
    fi
    
    print_success "Frontend tests completed"
}

# Function to run backend tests
run_backend_tests() {
    local SETTINGS_ONLY=$1
    
    print_header "Backend Tests"
    
    # Check if backend directory exists
    if [ ! -d "backend" ]; then
        print_error "Backend directory not found"
        return 1
    fi
    
    cd backend
    
    if [ "$SETTINGS_ONLY" = "true" ]; then
        print_info "Running Settings-specific backend tests..."
        
        if [ "$VERBOSE" = "true" ]; then
            python -m pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing --cov-report=html || true
        else
            python -m pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing || true
        fi
    else
        print_info "Running all backend tests..."
        
        if [ "$VERBOSE" = "true" ]; then
            python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html || true
        else
            python -m pytest tests/ -v --cov=. --cov-report=term-missing || true
        fi
    fi
    
    cd ..
    print_success "Backend tests completed"
}

# Function to check test files exist
check_test_files() {
    print_header "Verifying Test Files"
    
    local TEST_FILES=(
        "src/pages/SettingsPage.jsx"
        "src/pages/SettingsPage.css"
        "src/services/settingsService.js"
        "src/tests/SettingsPage.test.js"
        "src/tests/settingsService.test.js"
        "backend/settings_routes.py"
        "backend/tests/test_settings_routes.py"
    )
    
    local ALL_EXIST=true
    for file in "${TEST_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file exists"
        else
            print_error "$file is missing"
            ALL_EXIST=false
        fi
    done
    
    echo ""
    if [ "$ALL_EXIST" = "true" ]; then
        print_success "All required files are present"
    else
        print_error "Some required files are missing"
    fi
    echo ""
}

# Function to open coverage reports
open_coverage_reports() {
    print_header "Opening Coverage Reports"
    
    # Frontend coverage
    if [ -f "coverage/lcov-report/index.html" ]; then
        print_info "Opening frontend coverage report..."
        if command -v xdg-open > /dev/null; then
            xdg-open "coverage/lcov-report/index.html" &
        elif command -v open > /dev/null; then
            open "coverage/lcov-report/index.html"
        else
            print_error "Cannot open browser automatically. Please open coverage/lcov-report/index.html manually"
        fi
        print_success "Frontend coverage report opened"
    else
        print_error "Frontend coverage report not found. Run tests with coverage first."
    fi
    
    # Backend coverage
    if [ -f "backend/htmlcov/index.html" ]; then
        print_info "Opening backend coverage report..."
        if command -v xdg-open > /dev/null; then
            xdg-open "backend/htmlcov/index.html" &
        elif command -v open > /dev/null; then
            open "backend/htmlcov/index.html"
        else
            print_error "Cannot open browser automatically. Please open backend/htmlcov/index.html manually"
        fi
        print_success "Backend coverage report opened"
    else
        print_info "Backend coverage report not found (run backend tests with --cov-report=html)"
    fi
}

# Function to watch tests
watch_tests() {
    print_header "Watch Mode"
    print_info "Starting frontend tests in watch mode..."
    print_info "Press Ctrl+C to exit"
    echo ""
    
    npm test -- --watch --testPathPattern="Settings|settings"
}

# Main execution based on test type
check_test_files

case "$TEST_TYPE" in
    all)
        run_frontend_tests "false"
        run_backend_tests "false"
        ;;
    frontend)
        run_frontend_tests "false"
        ;;
    backend)
        run_backend_tests "false"
        ;;
    settings-only)
        run_frontend_tests "true"
        run_backend_tests "true"
        ;;
    coverage)
        print_info "Running tests with coverage..."
        run_frontend_tests "true"
        run_backend_tests "true"
        
        if [ "$OPEN_COVERAGE" = "true" ]; then
            open_coverage_reports
        fi
        ;;
    watch)
        watch_tests
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        echo "Valid options: all, frontend, backend, settings-only, coverage, watch"
        exit 1
        ;;
esac

# Summary
print_header "Test Run Summary"

if [ -f "coverage/lcov-report/index.html" ]; then
    print_success "Frontend coverage report: coverage/lcov-report/index.html"
fi

if [ -f "backend/htmlcov/index.html" ]; then
    print_success "Backend coverage report: backend/htmlcov/index.html"
fi

if [ -f "backend/coverage.xml" ]; then
    print_success "Backend coverage XML: backend/coverage.xml"
fi

echo ""
echo -e "${GREEN}Test run completed!${NC}"
echo ""

# Usage information
print_header "Usage"
echo "Examples:"
echo "  ./run_settings_tests.sh all                    # Run all tests"
echo "  ./run_settings_tests.sh frontend               # Frontend tests only"
echo "  ./run_settings_tests.sh backend                # Backend tests only"
echo "  ./run_settings_tests.sh settings-only          # Settings tests only"
echo "  ./run_settings_tests.sh coverage true          # Run with coverage and open reports"
echo "  ./run_settings_tests.sh watch                  # Watch mode for development"
echo "  ./run_settings_tests.sh all true               # Run with verbose output"
echo ""
