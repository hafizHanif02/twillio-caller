@echo off
echo Starting Twilio Caller Frontend on port 7001...
echo.

cd frontend

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo .env file created with default settings
    echo.
)

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting Vite dev server on port 7001...
echo Frontend will be available at http://localhost:7001
echo.

call npm run dev
