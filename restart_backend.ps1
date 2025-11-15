# Restart Backend Server Script
# Run this script to kill existing Flask server and start a new one

Write-Host "🔄 Restarting MediChain Backend Server..." -ForegroundColor Cyan

# Step 1: Find and kill processes on port 5000
Write-Host "`n1. Checking for processes on port 5000..." -ForegroundColor Yellow
$port5000 = netstat -ano | findstr :5000 | Select-String "LISTENING"
if ($port5000) {
    $pid = ($port5000 -split '\s+')[-1]
    Write-Host "   Found process $pid on port 5000" -ForegroundColor Yellow
    Write-Host "   Killing process $pid..." -ForegroundColor Yellow
    taskkill /F /PID $pid 2>$null
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Process killed" -ForegroundColor Green
} else {
    Write-Host "   ✅ No process found on port 5000" -ForegroundColor Green
}

# Step 2: Kill any Python processes that might be Flask
Write-Host "`n2. Checking for Python processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "   Found $($pythonProcs.Count) Python process(es)" -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        if ($proc.Path -like "*medichain*" -or $proc.MainWindowTitle -like "*app.py*") {
            Write-Host "   Killing Python process $($proc.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

# Step 3: Start the backend server
Write-Host "`n3. Starting backend server..." -ForegroundColor Yellow
Write-Host "   Navigate to: backend\app.py" -ForegroundColor Cyan
Write-Host "   Command: python app.py" -ForegroundColor Cyan
Write-Host "`n✅ Ready to start server!" -ForegroundColor Green
Write-Host "`nTo start manually, run:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor White
Write-Host "`nOr press any key to start automatically..." -ForegroundColor Cyan

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Start server in new window
Write-Host "`n🚀 Starting server in new window..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python app.py"

Write-Host "`n✅ Server starting in new window!" -ForegroundColor Green
Write-Host "   Check the new window for server logs" -ForegroundColor Cyan
Write-Host "   Server should be available at: http://localhost:5000" -ForegroundColor Cyan

