# Security Guidelines

## Overview

This document outlines security best practices and features implemented in the Twilio Voice Calling Application.

## Implemented Security Features

### 1. Twilio Webhook Signature Validation

**Location:** [backend/app/utils/security.py](backend/app/utils/security.py)

All webhook requests from Twilio are validated using the `X-Twilio-Signature` header to prevent request spoofing.

```python
# Webhook signature validation is enabled in production
if not settings.is_development:
    validate_twilio_request(request, form_data)
```

**Important:** Signature validation is disabled in development mode for easier testing but MUST be enabled in production.

### 2. Environment Variable Management

**Sensitive credentials are stored in `.env` files:**
- Twilio Account SID
- Twilio Auth Token
- Database credentials
- Secret keys

**Never commit `.env` files to version control.**

### 3. CORS Configuration

**Location:** [backend/app/main.py](backend/app/main.py)

CORS is configured to only allow requests from whitelisted origins:

```python
CORS_ORIGINS=http://localhost:5173,https://your-production-domain.com
```

### 4. Input Validation

**Location:** [backend/app/schemas.py](backend/app/schemas.py)

Phone numbers are validated using Pydantic validators to ensure E.164 format.

## Security Checklist for Production

### Backend

- [ ] Enable Twilio signature validation
- [ ] Use HTTPS for all webhook URLs
- [ ] Set strong SECRET_KEY in environment
- [ ] Use production database with strong password
- [ ] Enable database SSL connections
- [ ] Implement rate limiting on API endpoints
- [ ] Add authentication/authorization for API endpoints
- [ ] Disable FastAPI docs (`/docs`, `/redoc`) in production
- [ ] Set up proper logging (avoid logging sensitive data)
- [ ] Keep dependencies up to date
- [ ] Use environment-specific `.env` files

### Frontend

- [ ] Use environment variables for API URLs
- [ ] Implement Content Security Policy (CSP)
- [ ] Validate all user inputs
- [ ] Use HTTPS in production
- [ ] Keep dependencies up to date
- [ ] Minimize bundle size and remove unused code

### Infrastructure

- [ ] Use firewall rules to restrict database access
- [ ] Set up SSL/TLS certificates (Let's Encrypt)
- [ ] Enable database backups
- [ ] Monitor for suspicious activity
- [ ] Implement rate limiting at proxy/load balancer level
- [ ] Use separate credentials for dev/staging/production

## Twilio-Specific Security

### 1. Protect Your Auth Token

- **Never** hardcode Twilio credentials
- **Never** commit credentials to git
- Use environment variables
- Rotate tokens if compromised

### 2. Webhook Security

```python
# Always validate webhooks in production
from twilio.request_validator import RequestValidator

validator = RequestValidator(auth_token)
is_valid = validator.validate(url, params, signature)
```

### 3. Phone Number Validation

```python
# Validate phone numbers before making calls
@validator('to_number')
def validate_phone_number(cls, v):
    if not re.match(r'^\+[1-9]\d{1,14}$', v):
        raise ValueError('Invalid phone number format')
    return v
```

## Common Vulnerabilities to Avoid

### 1. SQL Injection

✅ **We use SQLAlchemy ORM** which prevents SQL injection by using parameterized queries.

### 2. XSS (Cross-Site Scripting)

✅ **React automatically escapes** values in JSX, preventing XSS.

### 3. CSRF (Cross-Site Request Forgery)

For production, consider implementing:
- CSRF tokens for state-changing operations
- SameSite cookie attributes

### 4. Denial of Service (DoS)

Implement:
- Rate limiting (e.g., 10 calls per minute per IP)
- Request timeout limits
- Connection limits

## Rate Limiting Example

```python
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/calls/outbound")
@limiter.limit("10/minute")
async def initiate_call(...):
    ...
```

## Monitoring and Logging

### What to Log

✅ Log:
- API requests and responses (without sensitive data)
- Authentication attempts
- Failed webhook validations
- Error stack traces
- Call events (initiated, completed, failed)

❌ Never log:
- Passwords or tokens
- Full API keys
- Credit card numbers
- Personal identifiable information (PII)

### Example Logging

```python
# Good
logger.info(f"Call initiated: {call_sid}")

# Bad - contains sensitive data
logger.info(f"Auth token: {settings.twilio_auth_token}")
```

## Incident Response

If credentials are compromised:

1. **Immediately** rotate Twilio Auth Token in Twilio Console
2. Update `.env` file with new credentials
3. Restart backend server
4. Review logs for suspicious activity
5. Check Twilio usage logs for unauthorized calls

## Additional Resources

- [Twilio Security Best Practices](https://www.twilio.com/docs/usage/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Contact

For security concerns or to report vulnerabilities, please create an issue on GitHub (do not include sensitive information in public issues).
