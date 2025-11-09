@echo off
REM Simple startup script for Ensina AI (Windows)

echo Starting Ensina AI...
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: No .env file found. Creating from template...
    copy .env.example .env
    echo Created .env file
    echo Please edit .env and add your ANTHROPIC_API_KEY
    echo.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Run the app
echo Starting Streamlit app...
echo.
streamlit run app.py
