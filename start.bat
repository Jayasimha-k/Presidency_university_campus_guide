@echo off
setlocal
cd /d "%~dp0"
if errorlevel 1 goto setup_failed

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if errorlevel 1 (
        where python >nul 2>nul
        if errorlevel 1 goto python_missing
        python -m venv ".venv"
    ) else (
        py -m venv ".venv"
    )
    if errorlevel 1 goto setup_failed
)

".venv\Scripts\python.exe" -c "import streamlit, sentence_transformers, chromadb, dotenv, PIL, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing the campus guide dependencies. This may take a few minutes...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto setup_failed
)

echo Starting the Presidency University Campus Guide...
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless=false --browser.gatherUsageStats=false
if errorlevel 1 goto launch_failed
exit /b 0

:python_missing
echo Python was not found. Install Python 3.10 or newer and enable "Add Python to PATH", then try again.
pause
exit /b 1

:setup_failed
echo Setup failed. Check your Python installation and internet connection, then try again.
pause
exit /b 1

:launch_failed
echo The campus guide stopped because of an error. Read the message above for details.
pause
exit /b 1
