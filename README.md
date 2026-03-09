# Twilio Voice Calling Application

A full-stack application for making and receiving phone calls via Twilio with real-time status updates.

## Features

- Make outbound calls from web interface
- Receive inbound calls to your Twilio number
- Real-time call status updates via WebSockets
- Call history and logs
- Modern React UI with real-time updates

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- Twilio Voice API
- WebSockets for real-time communication

**Frontend:**
- React 18
- Vite
- TypeScript
- Axios for HTTP requests

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose (for PostgreSQL)
- Twilio account with:
  - Account SID
  - Auth Token
  - Phone Number

## Setup Instructions

### 1. Clone and Navigate

```bash
cd "C:\Users\khana\twillio caller"
```

### 2. Set Up PostgreSQL

Start PostgreSQL using Docker Compose:

```bash
docker-compose up -d
```

Verify PostgreSQL is running:

```bash
docker ps
```

### 3. Backend Setup

#### Create Python Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your Twilio credentials:
```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number
DATABASE_URL=postgresql://twilio_user:twilio_password@localhost:5432/twilio_calls
WEBHOOK_BASE_URL=http://localhost:7000  # Will update with ngrok URL
SECRET_KEY=change-this-to-a-random-secret-key
CORS_ORIGINS=http://localhost:7001
```

#### Run Database Migrations

```bash
alembic upgrade head
```

#### Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 7000
```

The API will be available at [http://localhost:7000](http://localhost:7000)

API Documentation: [http://localhost:7000/docs](http://localhost:7000/docs)

### 4. Frontend Setup

Open a new terminal window:

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Configure Environment Variables

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. The default values should work for local development:
```bash
VITE_API_BASE_URL=http://localhost:7000
VITE_WS_URL=ws://localhost:7000/ws
```

#### Start the Frontend Development Server

```bash
npm run dev
```

The frontend will be available at [http://localhost:7001](http://localhost:7001)

### 5. Configure Twilio Webhooks (for receiving calls)

For local development, you need to expose your local server to the internet using ngrok:

#### Install ngrok

Download from [https://ngrok.com/download](https://ngrok.com/download)

#### Start ngrok

```bash
ngrok http 7000
```

#### Configure Twilio Console

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to Phone Numbers > Manage > Active Numbers
3. Click on your phone number
4. Under "Voice & Fax", set:
   - **A CALL COMES IN**: Webhook - `https://your-ngrok-url.ngrok.io/webhooks/voice/incoming` - HTTP POST
   - **PRIMARY HANDLER FAILS**: (optional)
5. Click **Save**

#### Update Backend .env

Update the `WEBHOOK_BASE_URL` in your backend `.env` file:

```bash
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

Restart the backend server after updating.

## Development Workflow

1. **Start PostgreSQL**: `docker-compose up -d`
2. **Start Backend**: `cd backend && uvicorn app.main:app --reload --port 7000`
3. **Start Frontend**: `cd frontend && npm run dev`
4. **Start ngrok** (for webhooks): `ngrok http 7000`
5. **Update Twilio webhooks** with ngrok URL

## Project Structure

```
twillio-caller/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── utils/             # Utilities
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   ├── models.py          # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (not in git)
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API and WebSocket clients
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Node dependencies
│   └── .env                   # Environment variables (not in git)
│
├── docker-compose.yml          # PostgreSQL setup
└── README.md                   # This file
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/calls/outbound` - Initiate outbound call
- `GET /api/calls/history` - Get call history
- `GET /api/calls/{call_sid}` - Get call details
- `POST /webhooks/voice/incoming` - Twilio incoming call webhook
- `POST /webhooks/voice/status` - Twilio call status webhook
- `WS /ws` - WebSocket connection for real-time updates

## Testing

### Test Outbound Call

1. Open the frontend at [http://localhost:7001](http://localhost:7001)
2. Enter a phone number (include country code, e.g., +1234567890)
3. Click "Call"
4. Watch real-time status updates

### Test Inbound Call

1. Make sure ngrok is running and webhooks are configured
2. Call your Twilio phone number from any phone
3. Watch the frontend for incoming call notification
4. Check call logs

## Troubleshooting

### Backend won't start

- Check if Python virtual environment is activated
- Verify PostgreSQL is running: `docker ps`
- Check `.env` file has all required variables
- Look for errors in terminal output

### Database connection errors

- Ensure PostgreSQL container is running: `docker-compose up -d`
- Check DATABASE_URL in `.env` matches docker-compose settings
- Try: `docker-compose down && docker-compose up -d`

### Webhooks not working

- Verify ngrok is running and URL is updated in Twilio console
- Check ngrok dashboard at [http://localhost:4040](http://localhost:4040)
- Ensure webhook URLs don't have trailing slashes
- Check backend logs for incoming webhook requests

### WebSocket connection fails

- Verify backend is running on port 7000
- Check frontend `.env` has correct WS_URL
- Look for CORS errors in browser console

## Database Management

### Create a new migration

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

```bash
cd backend
alembic upgrade head
```

### Rollback migration

```bash
cd backend
alembic downgrade -1
```

### Reset database

```bash
docker-compose down -v
docker-compose up -d
cd backend
alembic upgrade head
```

## Security Notes

- Never commit `.env` files to git
- Keep Twilio credentials secure
- Use different credentials for development and production
- Validate webhook signatures in production
- Use HTTPS in production (not HTTP)

## Next Steps

- Add user authentication
- Implement call recording
- Add call analytics dashboard
- Deploy to production (AWS, Heroku, etc.)
- Add SMS capabilities
- Implement conference calling

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
