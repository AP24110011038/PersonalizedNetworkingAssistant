@echo off
cd /d "%~dp0"
echo Installing required packages...
C:\Users\91939\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install -r requirements.txt
echo.
echo Starting FastAPI backend at http://127.0.0.1:8000
C:\Users\91939\AppData\Local\Python\pythoncore-3.14-64\python.exe -m uvicorn app.main:app --reload
pause
