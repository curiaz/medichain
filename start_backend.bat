@echo off
echo Starting MediChain Backend Server...
cd backend
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo Starting Flask server on http://localhost:5000...
python app.py
pause

