@echo off
echo ========================================
echo Restarting MediChain Backend Server
echo ========================================
echo.

echo Step 1: Killing processes on port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo   Found process %%a
    taskkill /F /PID %%a >nul 2>&1
    echo   Process killed
)
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting backend server...
echo.
cd backend
start "MediChain Backend Server" python app.py

echo.
echo ========================================
echo Server starting in new window!
echo Check the new window for server logs
echo Server URL: http://localhost:5000
echo ========================================
pause

