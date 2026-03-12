# Run all tests for dashboard branch
$env:CI = "true"
$ErrorActionPreference = "Stop"

Write-Host "Running Frontend Tests..." -ForegroundColor Cyan
try {
    npm test -- --watchAll=false --coverage --passWithNoTests --no-coverage 2>&1 | Out-File -FilePath frontend-test-results.txt
    Write-Host "Frontend tests completed. Results saved to frontend-test-results.txt" -ForegroundColor Green
} catch {
    Write-Host "Frontend tests failed: $_" -ForegroundColor Red
}

Write-Host "`nRunning Backend Tests..." -ForegroundColor Cyan
try {
    cd backend
    python -m pytest tests/ -v --tb=short 2>&1 | Out-File -FilePath ../backend-test-results.txt
    cd ..
    Write-Host "Backend tests completed. Results saved to backend-test-results.txt" -ForegroundColor Green
} catch {
    Write-Host "Backend tests failed: $_" -ForegroundColor Red
    cd ..
}

Write-Host "`nAll tests completed!" -ForegroundColor Yellow

