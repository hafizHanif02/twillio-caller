from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import math
from ..database import get_db
from ..schemas import (
    OutboundCallRequest,
    CallResponse,
    CallHistoryResponse,
    ErrorResponse,
    TokenResponse
)
from ..services.call_service import call_service
from ..services.twilio_service import twilio_service
from ..utils.logger import logger

router = APIRouter()


@router.get("/token", response_model=TokenResponse)
async def generate_access_token(
    identity: Optional[str] = Query(None, description="User identity for the token")
):
    """
    Generate an access token for Twilio Voice SDK in the browser.

    Args:
        identity: Optional user identity. Defaults to "web_user" if not provided.

    Returns:
        TokenResponse with JWT token and expiration info

    Raises:
        HTTPException: If token generation fails
    """
    try:
        # Use provided identity or default
        user_identity = identity or "web_user"
        ttl = 3600  # Token valid for 1 hour

        logger.info(f"Generating access token for identity: {user_identity}")

        # Generate token using Twilio service
        token = twilio_service.generate_access_token(identity=user_identity, ttl=ttl)

        return TokenResponse(
            token=token,
            identity=user_identity,
            expires_in=ttl
        )

    except Exception as e:
        logger.error(f"Error generating access token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate access token: {str(e)}"
        )


@router.post("/outbound", response_model=CallResponse, status_code=201)
async def initiate_outbound_call(
    request: OutboundCallRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call.

    Args:
        request: Outbound call request with phone number
        db: Database session

    Returns:
        CallResponse with call details

    Raises:
        HTTPException: If call creation fails
    """
    try:
        logger.info(f"Initiating outbound call to {request.to_number}")

        call_log = await call_service.initiate_outbound_call(
            to_number=request.to_number,
            db=db
        )

        return CallResponse(
            call_sid=call_log.call_sid,
            direction=call_log.direction,
            from_number=call_log.from_number,
            to_number=call_log.to_number,
            status=call_log.status,
            start_time=call_log.start_time,
            end_time=call_log.end_time,
            duration=call_log.duration,
            recording_url=call_log.recording_url,
            price=float(call_log.price) if call_log.price else None,
            price_unit=call_log.price_unit,
            metadata=call_log.call_metadata or {},
            created_at=call_log.created_at,
            updated_at=call_log.updated_at
        )

    except Exception as e:
        logger.error(f"Error initiating outbound call: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate call: {str(e)}"
        )


@router.get("/history", response_model=CallHistoryResponse)
async def get_call_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    direction: Optional[str] = Query(None, description="Filter by direction (inbound/outbound)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get call history with pagination and filtering.

    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page
        direction: Filter by call direction
        status: Filter by call status
        db: Database session

    Returns:
        CallHistoryResponse with paginated call list
    """
    try:
        # Calculate skip based on page
        skip = (page - 1) * page_size

        # Get calls and total count
        calls, total = call_service.get_call_history(
            db=db,
            skip=skip,
            limit=page_size,
            direction=direction,
            status=status
        )

        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # Convert to response models
        call_responses = [
            CallResponse(
                call_sid=call.call_sid,
                direction=call.direction,
                from_number=call.from_number,
                to_number=call.to_number,
                status=call.status,
                start_time=call.start_time,
                end_time=call.end_time,
                duration=call.duration,
                recording_url=call.recording_url,
                price=float(call.price) if call.price else None,
                price_unit=call.price_unit,
                metadata=call.call_metadata or {},
                created_at=call.created_at,
                updated_at=call.updated_at
            )
            for call in calls
        ]

        return CallHistoryResponse(
            calls=call_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error fetching call history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch call history: {str(e)}"
        )


@router.get("/{call_sid}", response_model=CallResponse)
async def get_call_details(
    call_sid: str,
    sync_from_twilio: bool = Query(False, description="Sync latest data from Twilio"),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific call.

    Args:
        call_sid: Twilio call SID
        sync_from_twilio: If True, fetch latest data from Twilio API
        db: Database session

    Returns:
        CallResponse with call details

    Raises:
        HTTPException: If call not found
    """
    try:
        if sync_from_twilio:
            # Sync from Twilio API
            call_log = await call_service.sync_call_from_twilio(call_sid, db)
        else:
            # Get from database only
            call_log = call_service.get_call_by_sid(call_sid, db)

        if not call_log:
            raise HTTPException(
                status_code=404,
                detail=f"Call {call_sid} not found"
            )

        return CallResponse(
            call_sid=call_log.call_sid,
            direction=call_log.direction,
            from_number=call_log.from_number,
            to_number=call_log.to_number,
            status=call_log.status,
            start_time=call_log.start_time,
            end_time=call_log.end_time,
            duration=call_log.duration,
            recording_url=call_log.recording_url,
            price=float(call_log.price) if call_log.price else None,
            price_unit=call_log.price_unit,
            metadata=call_log.call_metadata or {},
            created_at=call_log.created_at,
            updated_at=call_log.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call details for {call_sid}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch call details: {str(e)}"
        )


@router.get("/statistics/summary")
async def get_call_statistics(db: Session = Depends(get_db)):
    """
    Get call statistics summary.

    Args:
        db: Database session

    Returns:
        Dictionary with call statistics
    """
    try:
        stats = call_service.get_call_statistics(db)
        return stats

    except Exception as e:
        logger.error(f"Error fetching call statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )
