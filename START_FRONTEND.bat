@echo off
cd /d "%~dp0"
echo Starting Streamlit frontend at http://localhost:8501
C:\Users\91939\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run frontend\streamlit_app.py
pause
