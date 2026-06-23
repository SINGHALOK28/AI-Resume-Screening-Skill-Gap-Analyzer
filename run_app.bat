@echo off
echo Starting AI Resume Screening System...
echo.
cd /d "%~dp0"

IF EXIST ".venv\Scripts\streamlit.exe" (
    echo [INFO] Found virtual environment.
    ".venv\Scripts\streamlit.exe" run app.py
) ELSE (
    echo [INFO] Virtual environment not found. Using global Streamlit.
    streamlit run app.py
)
pause
