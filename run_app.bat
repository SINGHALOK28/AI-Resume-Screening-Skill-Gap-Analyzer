@echo off
echo Starting AI Resume Screening System...
echo.
cd /d "%~dp0"
streamlit run frontend/streamlit_app.py
pause

