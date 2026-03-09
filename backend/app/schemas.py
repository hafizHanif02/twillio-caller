from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


class OutboundCallRequest(BaseModel):
    """Request model for initiating an outbound call."""
    to_number: str = Field(..., description="Phone number to call (E.164 format recommended)")

    @validator('to_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', v)

        # Check if it starts with + (international format)
        if not cleaned.startswith('+'):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = f'+1{cleaned}'
            else:
                raise ValueError('Phone number must be in E.164 format (e.g., +1234567890)')

        # Validate format
        if not re.match(r'^\+[1-9]\d{1,14}$', cleaned):
            raise ValueError('Invalid phone number format. Use E.164 format (e.g., +1234567890)')

        return cleaned


class CallResponse(BaseModel):
    """Response model for call operations."""
    call_sid: str
    direction: str
    from_number: str
    to_number: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    price: Optional[float] = None
    price_unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallHistoryResponse(BaseModel):
    """Response model for call history with pagination."""
    calls: list[CallResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="Message type (e.g., call.initiated, call.ringing)")
    timestamp: str
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for access token generation."""
    token: str = Field(..., description="JWT access token for Twilio Voice SDK")
    identity: str = Field(..., description="User identity associated with the token")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "identity": "web_user_123",
                "expires_in": 3600
            }
        }
