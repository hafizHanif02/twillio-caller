# Quick Start Guide

Get your Twilio calling app running in minutes!

## Prerequisites

Before you begin, make sure you have:

- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Docker Desktop running (for PostgreSQL)
- ✅ Twilio account with Account SID, Auth Token, and Phone Number
- ✅ ngrok installed (download from https://ngrok.com/download)

## Step 1: Start PostgreSQL

Open a terminal and run:

```bash
cd "C:\Users\khana\twillio caller"
docker-compose up -d
```

Verify it's running:
```bash
docker ps
```

You should see a `twilio_postgres` container running.

## Step 2: Configure Backend

1. Navigate to the backend folder and copy the environment template:
   ```bash
   cd backend
   copy .env.example .env
   ```

2. Edit `backend\.env` with your Twilio credentials:
   ```bash
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

3. Keep other settings as default for now.

## Step 3: Start Backend (Port 7000)

**Option A - Using the startup script (Recommended):**

Double-click `start-backend.bat` in the root folder.

**Option B - Manual:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 7000
```

✅ Backend should now be running at **http://localhost:7000**

Test it: Open http://localhost:7000/docs in your browser

## Step 4: Start Frontend (Port 7001)

Open a **new terminal** and:

**Option A - Using the startup script (Recommended):**

Double-click `start-frontend.bat` in the root folder.

**Option B - Manual:**

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend should now be running at **http://localhost:7001**

Open http://localhost:7001 in your browser - you should see the Twilio Voice Caller interface!

## Step 5: Test Outbound Calls

1. Go to http://localhost:7001
2. Enter a phone number in E.164 format (e.g., +12025551234)
3. Click "Make Call"
4. Your phone should ring!
5. Watch the real-time status updates in the UI

## Step 6: Configure Incoming Calls (Optional)

To receive calls, you need to expose your backend to the internet:

1. **Start ngrok:**

   Double-click `start-ngrok.bat` or run:
   ```bash
   ngrok http 7000
   ```

2. **Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

3. **Update backend\.env:**
   ```bash
   WEBHOOK_BASE_URL=https://abc123.ngrok.io
   ```

4. **Restart the backend** (Ctrl+C and start again)

5. **Configure Twilio Console:**
   - Go to https://console.twilio.com/
   - Navigate to Phone Numbers → Manage → Active Numbers
   - Click your phone number
   - Under "Voice & Fax", set:
     - **A CALL COMES IN**: Webhook
     - **URL**: `https://abc123.ngrok.io/webhooks/voice/incoming`
     - **HTTP**: POST
   - Click Save

6. **Test it:** Call your Twilio number and watch the incoming call notification appear in the UI!

## Ports Summary

- **Frontend**: http://localhost:7001
- **Backend API**: http://localhost:7000
- **Backend Docs**: http://localhost:7000/docs
- **PostgreSQL**: localhost:5432
- **ngrok Dashboard**: http://localhost:4040 (when ngrok is running)

## Common Issues

### "Port already in use"
- Make sure nothing else is running on ports 7000 or 7001
- Kill any existing processes: `netstat -ano | findstr :7000`

### "Database connection error"
- Ensure Docker Desktop is running
- Check PostgreSQL is running: `docker ps`
- Restart PostgreSQL: `docker-compose restart`

### "Module not found" (Python)
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### "Cannot find module" (Node)
- Delete `node_modules` and reinstall: `npm install`

### WebSocket not connecting
- Check backend is running on port 7000
- Check frontend `.env` has `VITE_WS_URL=ws://localhost:7000/ws`
- Look for errors in browser console (F12)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [SECURITY.md](SECURITY.md) for production deployment
- Check [TESTING.md](TESTING.md) for testing guidelines

## Quick Reference Commands

**Start all services:**
```bash
# Terminal 1 - PostgreSQL
docker-compose up -d

# Terminal 2 - Backend
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 7000

# Terminal 3 - Frontend
cd frontend && npm run dev

# Terminal 4 - ngrok (optional, for incoming calls)
ngrok http 7000
```

**Stop all services:**
```bash
# Stop backend: Ctrl+C in backend terminal
# Stop frontend: Ctrl+C in frontend terminal
# Stop ngrok: Ctrl+C in ngrok terminal
# Stop PostgreSQL: docker-compose down
```

## Success! 🎉

You should now have:
- ✅ Backend running on port 7000
- ✅ Frontend running on port 7001
- ✅ PostgreSQL database running
- ✅ Ability to make outbound calls
- ✅ (Optional) Ability to receive inbound calls via ngrok

Visit http://localhost:7001 and start making calls!
