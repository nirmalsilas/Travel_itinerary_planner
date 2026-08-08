@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

if not exist ".env" (
    echo Please create a .env file with GROQ_API_KEY and PEXELS_API_KEY.
    pause
    exit /b 1
)

start "" http://127.0.0.1:8000
.venv\Scripts\python.exe -m uvicorn app:app