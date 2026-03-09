@echo off
echo Starting ngrok tunnel for port 7000...
echo.
echo This will expose your backend at a public URL for Twilio webhooks
echo.
echo After ngrok starts:
echo 1. Copy the https URL (e.g., https://abc123.ngrok.io)
echo 2. Update backend\.env file: WEBHOOK_BASE_URL=https://abc123.ngrok.io
echo 3. Update Twilio Console webhooks with this URL
echo.

ngrok http 7000
