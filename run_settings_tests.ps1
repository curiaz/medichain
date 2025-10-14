# Settings Feature Test Runner
# Comprehensive test execution script for local development

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('all', 'frontend', 'backend', 'settings-only', 'coverage', 'watch')]
    [string]$TestType = 'all',
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$OpenCoverage
)

$ErrorActionPreference = "Continue"

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "================================================" "Cyan"
    Write-ColorOutput "  $Title" "Cyan"
    Write-ColorOutput "================================================" "Cyan"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "→ $Message" "Yellow"
}

# Check if we're in the correct directory
if (-not (Test-Path "package.json")) {
    Write-Error "Please run this script from the medichain root directory"
    exit 1
}

Write-Header "MediChain Settings Feature Test Suite"
Write-Info "Test Type: $TestType"
Write-Info "Verbose: $Verbose"
Write-Host ""

# Function to run frontend tests
function Run-FrontendTests {
    param([bool]$SettingsOnly = $false)
    
    Write-Header "Frontend Tests"
    
    if ($SettingsOnly) {
        Write-Info "Running Settings-specific frontend tests..."
        
        # SettingsPage component tests
        Write-Host ""
        Write-ColorOutput "Testing SettingsPage Component..." "Cyan"
        npm test -- src/tests/SettingsPage.test.js --coverage --watchAll=false --verbose
        
        # settingsService tests
        Write-Host ""
        Write-ColorOutput "Testing settingsService..." "Cyan"
        npm test -- src/tests/settingsService.test.js --coverage --watchAll=false --verbose
        
        # Combined coverage
        Write-Host ""
        Write-ColorOutput "Generating Combined Coverage Report..." "Cyan"
        npm test -- --testPathPattern="Settings|settings" --coverage --watchAll=false --collectCoverageFrom="src/pages/SettingsPage.jsx,src/services/settingsService.js"
    } else {
        Write-Info "Running all frontend tests..."
        npm test -- --coverage --watchAll=false
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend tests completed successfully"
    } else {
        Write-Error "Some frontend tests failed (exit code: $LASTEXITCODE)"
    }
}

# Function to run backend tests
function Run-BackendTests {
    param([bool]$SettingsOnly = $false)
    
    Write-Header "Backend Tests"
    
    # Check if backend directory exists
    if (-not (Test-Path "backend")) {
        Write-Error "Backend directory not found"
        return
    }
    
    Push-Location backend
    
    try {
        if ($SettingsOnly) {
            Write-Info "Running Settings-specific backend tests..."
            
            if ($Verbose) {
                python -m pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing --cov-report=html
            } else {
                python -m pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing
            }
        } else {
            Write-Info "Running all backend tests..."
            
            if ($Verbose) {
                python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
            } else {
                python -m pytest tests/ -v --cov=. --cov-report=term-missing
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend tests completed successfully"
        } else {
            Write-Error "Some backend tests failed (exit code: $LASTEXITCODE)"
        }
    } finally {
        Pop-Location
    }
}

# Function to check test files exist
function Check-TestFiles {
    Write-Header "Verifying Test Files"
    
    $testFiles = @(
        "src/pages/SettingsPage.jsx",
        "src/pages/SettingsPage.css",
        "src/services/settingsService.js",
        "src/tests/SettingsPage.test.js",
        "src/tests/settingsService.test.js",
        "backend/settings_routes.py",
        "backend/tests/test_settings_routes.py"
    )
    
    $allExist = $true
    foreach ($file in $testFiles) {
        if (Test-Path $file) {
            Write-Success "$file exists"
        } else {
            Write-Error "$file is missing"
            $allExist = $false
        }
    }
    
    Write-Host ""
    if ($allExist) {
        Write-Success "All required files are present"
    } else {
        Write-Error "Some required files are missing"
    }
    Write-Host ""
}

# Function to open coverage reports
function Open-CoverageReports {
    Write-Header "Opening Coverage Reports"
    
    # Frontend coverage
    if (Test-Path "coverage/lcov-report/index.html") {
        Write-Info "Opening frontend coverage report..."
        Start-Process "coverage/lcov-report/index.html"
        Write-Success "Frontend coverage report opened"
    } else {
        Write-Error "Frontend coverage report not found. Run tests with coverage first."
    }
    
    # Backend coverage
    if (Test-Path "backend/htmlcov/index.html") {
        Write-Info "Opening backend coverage report..."
        Start-Process "backend/htmlcov/index.html"
        Write-Success "Backend coverage report opened"
    } else {
        Write-Info "Backend coverage report not found (run backend tests with --cov-report=html)"
    }
}

# Function to watch tests
function Watch-Tests {
    Write-Header "Watch Mode"
    Write-Info "Starting frontend tests in watch mode..."
    Write-Info "Press Ctrl+C to exit"
    Write-Host ""
    
    npm test -- --watch --testPathPattern="Settings|settings"
}

# Main execution based on test type
Check-TestFiles

switch ($TestType) {
    'all' {
        Run-FrontendTests -SettingsOnly $false
        Run-BackendTests -SettingsOnly $false
    }
    'frontend' {
        Run-FrontendTests -SettingsOnly $false
    }
    'backend' {
        Run-BackendTests -SettingsOnly $false
    }
    'settings-only' {
        Run-FrontendTests -SettingsOnly $true
        Run-BackendTests -SettingsOnly $true
    }
    'coverage' {
        Write-Info "Running tests with coverage..."
        Run-FrontendTests -SettingsOnly $true
        Run-BackendTests -SettingsOnly $true
        
        if ($OpenCoverage) {
            Open-CoverageReports
        }
    }
    'watch' {
        Watch-Tests
    }
}

# Summary
Write-Header "Test Run Summary"

if (Test-Path "coverage/lcov-report/index.html") {
    Write-Success "Frontend coverage report: coverage/lcov-report/index.html"
}

if (Test-Path "backend/htmlcov/index.html") {
    Write-Success "Backend coverage report: backend/htmlcov/index.html"
}

if (Test-Path "backend/coverage.xml") {
    Write-Success "Backend coverage XML: backend/coverage.xml"
}

Write-Host ""
Write-ColorOutput "Test run completed!" "Green"
Write-Host ""

# Usage information
Write-Header "Usage"
Write-Host "Examples:"
Write-Host "  .\run_settings_tests.ps1 -TestType all              # Run all tests"
Write-Host "  .\run_settings_tests.ps1 -TestType frontend         # Frontend tests only"
Write-Host "  .\run_settings_tests.ps1 -TestType backend          # Backend tests only"
Write-Host "  .\run_settings_tests.ps1 -TestType settings-only    # Settings tests only"
Write-Host "  .\run_settings_tests.ps1 -TestType coverage -OpenCoverage  # Run with coverage and open reports"
Write-Host "  .\run_settings_tests.ps1 -TestType watch            # Watch mode for development"
Write-Host "  .\run_settings_tests.ps1 -TestType all -Verbose     # Run with verbose output"
Write-Host ""
