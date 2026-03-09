@echo off
echo Starting Twilio Caller Backend on port 7000...
echo.

cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit backend\.env with your Twilio credentials!
    echo.
    pause
)

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on port 7000...
echo API will be available at http://localhost:7000
echo API Docs will be available at http://localhost:7000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 7000
