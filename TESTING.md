# Testing Guide

## Overview

This document provides guidelines for testing the Twilio Voice Calling Application.

## Testing Strategy

### 1. Backend Testing

#### Unit Tests

Test individual functions and services in isolation.

**Example: Testing Twilio Service**

```python
# tests/test_twilio_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.twilio_service import TwilioService

@pytest.fixture
def twilio_service():
    return TwilioService()

def test_make_outbound_call(twilio_service):
    with patch.object(twilio_service.client.calls, 'create') as mock_create:
        mock_create.return_value = Mock(
            sid='CA1234567890',
            status='queued',
            date_created='2024-01-01T00:00:00Z'
        )

        result = twilio_service.make_outbound_call('+1234567890')

        assert result['call_sid'] == 'CA1234567890'
        assert result['status'] == 'queued'
        mock_create.assert_called_once()
```

#### Integration Tests

Test API endpoints with database.

```python
# tests/test_api_calls.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_call_history():
    response = client.get("/api/calls/history")
    assert response.status_code == 200
    assert 'calls' in response.json()
    assert 'total' in response.json()
```

#### Webhook Testing

Test webhook signature validation:

```python
# tests/test_webhooks.py
def test_webhook_signature_validation():
    # Test with valid signature
    response = client.post(
        "/webhooks/voice/status",
        data={"CallSid": "CA123", "CallStatus": "completed"},
        headers={"X-Twilio-Signature": "valid_signature"}
    )
    # Should succeed with valid signature
    assert response.status_code == 200
```

### 2. Frontend Testing

#### Component Tests

```typescript
// tests/CallButton.test.tsx
import { render, screen, fireEvent } from '@testing/library/react';
import { CallButton } from '../components/CallButton';

test('should initiate call when button is clicked', async () => {
  render(<CallButton />);

  const input = screen.getByPlaceholderText(/enter phone number/i);
  const button = screen.getByText(/make call/i);

  fireEvent.change(input, { target: { value: '+1234567890' } });
  fireEvent.click(button);

  // Assert that API was called
  // ...
});
```

### 3. End-to-End Testing

Use Playwright or Cypress for E2E tests.

```typescript
// e2e/call-flow.spec.ts
test('complete call flow', async ({ page }) => {
  await page.goto('http://localhost:7001');

  // Enter phone number
  await page.fill('input[type="tel"]', '+1234567890');

  // Click call button
  await page.click('button:has-text("Make Call")');

  // Wait for call to be initiated
  await page.waitForSelector('.call-status-container');

  // Verify call status is displayed
  const status = await page.textContent('.status-badge');
  expect(status).toBeTruthy();
});
```

## Manual Testing Checklist

### Backend API

- [ ] GET `/health` - Health check returns 200
- [ ] POST `/api/calls/outbound` - Initiates outbound call
- [ ] GET `/api/calls/history` - Returns call history
- [ ] GET `/api/calls/{call_sid}` - Returns call details
- [ ] POST `/webhooks/voice/incoming` - Handles incoming call
- [ ] POST `/webhooks/voice/status` - Processes status updates
- [ ] WS `/ws` - WebSocket connection established

### Frontend

- [ ] WebSocket connects on page load
- [ ] Connection status indicator works
- [ ] Phone number input validates format
- [ ] Make call button disabled when input is empty
- [ ] Call status updates in real-time
- [ ] Call history table displays correctly
- [ ] Filters work (direction, status)
- [ ] Incoming call modal appears
- [ ] Error messages display correctly

### Integration Testing

#### Test Outbound Call Flow

1. Start backend: `cd backend && uvicorn app.main:app --reload --port 7000`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to `http://localhost:7001`
4. Enter a valid phone number (e.g., your phone)
5. Click "Make Call"
6. Verify:
   - Call appears in call history
   - Status updates in real-time
   - Phone rings
   - Call can be answered
   - Duration timer works
   - Call completes successfully

#### Test Inbound Call Flow

1. Ensure ngrok is running: `ngrok http 7000`
2. Configure Twilio webhook with ngrok URL
3. Call your Twilio number from a phone
4. Verify:
   - Incoming call notification appears
   - Call appears in call history
   - TwiML response plays
   - Status updates correctly
   - Call can be completed

### WebSocket Testing

Test WebSocket connection and real-time updates:

1. Open browser DevTools (Network tab → WS)
2. Reload page
3. Verify WebSocket connection to `ws://localhost:7000/ws`
4. Make a call
5. Observe WebSocket messages:
   - `connection.established`
   - `call.initiated`
   - `call.ringing`
   - `call.answered` / `call.completed`
6. Verify heartbeat pings every 30 seconds

## Testing with Twilio

### Twilio Test Credentials

Twilio provides test credentials for development:

```
Account SID: AC...
Auth Token: test_token
```

### Test Phone Numbers

Use Twilio's magic phone numbers for testing:

- `+15005550006` - Valid number (returns success)
- `+15005550001` - Invalid number (returns error)
- `+15005550007` - Busy line
- `+15005550008` - No answer
- `+15005550009` - Number does not exist

Example test:

```python
def test_call_to_invalid_number():
    response = client.post(
        "/api/calls/outbound",
        json={"to_number": "+15005550001"}
    )
    # Should fail with invalid number
    assert response.status_code in [400, 500]
```

## Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class CallApiUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_call_history(self):
        self.client.get("/api/calls/history")

    @task(2)
    def health_check(self):
        self.client.get("/health")
```

Run load test:

```bash
locust -f locustfile.py --host=http://localhost:7000
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: |
          cd backend
          pytest

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
```

## Test Coverage

Aim for:
- Backend: >80% code coverage
- Frontend: >70% code coverage
- Critical paths: 100% coverage (authentication, payment, etc.)

Generate coverage report:

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html

# Frontend
cd frontend
npm test -- --coverage
```

## Debugging Tips

### Backend

1. Add breakpoints in VS Code
2. Use FastAPI's interactive docs: `http://localhost:7000/docs`
3. Check logs in terminal
4. Use `logger.debug()` for detailed logging

### Frontend

1. Use React DevTools browser extension
2. Check browser console for errors
3. Inspect WebSocket messages in Network tab
4. Use Redux DevTools for state debugging (if using Redux)

### Twilio

1. Check Twilio Console → Monitor → Logs
2. Use Twilio CLI: `twilio api:core:calls:list`
3. Enable debug logs: `twilio api:core:accounts:update --voice-trace-enabled`

## Common Issues

### Webhook Not Receiving Requests

- Verify ngrok is running
- Check Twilio Console webhook URL
- Ensure webhook URL has correct path
- Check for firewall/network issues

### WebSocket Connection Failed

- Verify backend is running on port 7000
- Check CORS settings
- Verify WS_URL in frontend .env

### Call Not Connecting

- Verify Twilio credentials are correct
- Check phone number format (E.164)
- Ensure you have funds in Twilio account
- Check Twilio account isn't in trial mode restrictions

## Resources

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Twilio Testing](https://www.twilio.com/docs/iam/test-credentials)
- [Pytest Documentation](https://docs.pytest.org/)
