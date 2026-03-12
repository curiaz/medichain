#!/usr/bin/env pwsh
# Run GitHub Actions CI locally using Act

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Run CI Workflow Locally with Act" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Act is installed
$actInstalled = Get-Command act -ErrorAction SilentlyContinue

if (-not $actInstalled) {
    Write-Host "❌ Act is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Act, choose one of these options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Using Chocolatey:" -ForegroundColor White
    Write-Host "     choco install act-cli" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Using Scoop:" -ForegroundColor White
    Write-Host "     scoop install act" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Manual download:" -ForegroundColor White
    Write-Host "     https://github.com/nektos/act/releases" -ForegroundColor Gray
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    Write-Host ""
    
    # Offer to use the alternative test script
    Write-Host "Alternative: Run our local test script instead?" -ForegroundColor Cyan
    $response = Read-Host "Run test_ci_locally.ps1? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        & .\test_ci_locally.ps1
    }
    exit 1
}

Write-Host "✓ Act is installed: $(act --version)" -ForegroundColor Green
Write-Host ""

# Show available jobs
Write-Host "Available CI jobs:" -ForegroundColor Yellow
act -l
Write-Host ""

# Menu for user
Write-Host "What would you like to run?" -ForegroundColor Cyan
Write-Host "  1. All jobs (full CI pipeline)" -ForegroundColor White
Write-Host "  2. Backend tests only" -ForegroundColor White
Write-Host "  3. Frontend tests only" -ForegroundColor White
Write-Host "  4. Backend linting only" -ForegroundColor White
Write-Host "  5. Frontend linting only" -ForegroundColor White
Write-Host "  6. Build frontend only" -ForegroundColor White
Write-Host "  7. Security scan only" -ForegroundColor White
Write-Host "  8. Dry run (show what would execute)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-8)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running all CI jobs..." -ForegroundColor Green
        act push
    }
    "2" {
        Write-Host ""
        Write-Host "Running backend tests..." -ForegroundColor Green
        act push -j backend-tests
    }
    "3" {
        Write-Host ""
        Write-Host "Running frontend tests..." -ForegroundColor Green
        act push -j frontend-tests
    }
    "4" {
        Write-Host ""
        Write-Host "Running backend linting..." -ForegroundColor Green
        act push -j lint-backend
    }
    "5" {
        Write-Host ""
        Write-Host "Running frontend linting..." -ForegroundColor Green
        act push -j lint-frontend
    }
    "6" {
        Write-Host ""
        Write-Host "Building frontend..." -ForegroundColor Green
        act push -j build-frontend
    }
    "7" {
        Write-Host ""
        Write-Host "Running security scan..." -ForegroundColor Green
        act push -j security-scan
    }
    "8" {
        Write-Host ""
        Write-Host "Dry run - showing execution plan..." -ForegroundColor Green
        act push -n
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Running dry run..." -ForegroundColor Yellow
        act push -n
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
