#!/usr/bin/env pwsh
# Local CI Test Script
# Run this before pushing to test what CI will check

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MediChain Local CI Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# Test Backend
Write-Host "[1/4] Testing Backend..." -ForegroundColor Yellow
Push-Location backend
try {
    Write-Host "  - Installing dependencies..." -ForegroundColor Gray
    pip install -q -r requirements.txt
    pip install -q pytest pytest-cov
    
    Write-Host "  - Running pytest..." -ForegroundColor Gray
    python -m pytest tests/ -v --cov=app --cov-report=term
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Backend tests failed!" -ForegroundColor Red
        $ErrorCount++
    } else {
        Write-Host "  ✓ Backend tests passed!" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Backend test error: $_" -ForegroundColor Red
    $ErrorCount++
} finally {
    Pop-Location
}

Write-Host ""

# Test Frontend
Write-Host "[2/4] Testing Frontend..." -ForegroundColor Yellow
try {
    Write-Host "  - Installing dependencies..." -ForegroundColor Gray
    npm ci --silent
    
    Write-Host "  - Running tests..." -ForegroundColor Gray
    npm test -- --coverage --watchAll=false --passWithNoTests
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Frontend tests failed!" -ForegroundColor Red
        $ErrorCount++
    } else {
        Write-Host "  ✓ Frontend tests passed!" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Frontend test error: $_" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""

# Lint Backend
Write-Host "[3/4] Linting Backend..." -ForegroundColor Yellow
Push-Location backend
try {
    Write-Host "  - Installing linting tools..." -ForegroundColor Gray
    pip install -q flake8 black isort
    
    Write-Host "  - Running flake8..." -ForegroundColor Gray
    flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Flake8 found errors!" -ForegroundColor Red
        $ErrorCount++
    } else {
        Write-Host "  ✓ Flake8 passed!" -ForegroundColor Green
    }
    
    Write-Host "  - Checking code formatting..." -ForegroundColor Gray
    black --check app 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠ Code needs formatting (run: black app)" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ Code formatting passed!" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Linting error: $_" -ForegroundColor Red
    $ErrorCount++
} finally {
    Pop-Location
}

Write-Host ""

# Build Frontend
Write-Host "[4/4] Building Frontend..." -ForegroundColor Yellow
try {
    Write-Host "  - Running build..." -ForegroundColor Gray
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Frontend build failed!" -ForegroundColor Red
        $ErrorCount++
    } else {
        Write-Host "  ✓ Frontend build successful!" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Build error: $_" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($ErrorCount -eq 0) {
    Write-Host "  ✓ All checks passed!" -ForegroundColor Green
    Write-Host "  You're ready to push!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "  ✗ $ErrorCount check(s) failed!" -ForegroundColor Red
    Write-Host "  Please fix errors before pushing." -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
