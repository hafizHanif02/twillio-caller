from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models import CallLog
from ..services.twilio_service import twilio_service
from ..services.websocket_manager import websocket_manager
from ..utils.logger import logger
from ..utils.security import twilio_validator

router = APIRouter()


@router.post("/voice/incoming")
async def handle_incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
    Direction: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle incoming Twilio voice calls.

    This webhook is triggered when a call comes in to your Twilio number.
    Returns TwiML instructions for how to handle the call.
    """
    try:
        logger.info(f"Incoming call webhook: {CallSid} from {From} to {To}, status: {CallStatus}")

        # Validate Twilio signature in production
        if not twilio_validator.validator.validate(
            str(request.url),
            await request.form(),
            request.headers.get('X-Twilio-Signature', '')
        ):
            logger.warning(f"Invalid Twilio signature for incoming call {CallSid}")
            if not request.app.state.settings.is_development:
                raise HTTPException(status_code=403, detail="Invalid signature")

        # Create or update call log in database
        call_log = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()

        if not call_log:
            call_log = CallLog(
                call_sid=CallSid,
                direction="inbound",
                from_number=From,
                to_number=To,
                status=CallStatus,
                start_time=datetime.utcnow() if CallStatus == "ringing" else None
            )
            db.add(call_log)
        else:
            call_log.status = CallStatus
            if CallStatus == "in-progress" and not call_log.start_time:
                call_log.start_time = datetime.utcnow()

        db.commit()

        # Broadcast incoming call event to WebSocket clients
        await websocket_manager.broadcast_call_event(
            event_type="incoming.call",
            call_sid=CallSid,
            status=CallStatus,
            direction="inbound",
            from_number=From,
            to_number=To
        )

        # Generate TwiML response
        # You can customize this to forward to a specific number or play a message
        twiml = twilio_service.generate_incoming_twiml(
            forward_to=None,  # Set to a number to forward calls
            message="Thank you for calling. This is a demo Twilio application."
        )

        logger.info(f"Returning TwiML for call {CallSid}")

        return Response(
            content=twiml,
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"Error handling incoming call {CallSid}: {str(e)}")
        # Return a simple TwiML response even on error
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>'
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/voice/status")
async def handle_call_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(None),
    To: str = Form(None),
    Direction: str = Form(None),
    Duration: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
    CallDuration: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle Twilio call status updates.

    This webhook receives status updates for both inbound and outbound calls.
    Statuses include: initiated, ringing, in-progress, completed, busy, failed, no-answer
    """
    try:
        logger.info(f"Call status webhook: {CallSid} status: {CallStatus}")

        # Validate Twilio signature in production
        if not twilio_validator.validator.validate(
            str(request.url),
            await request.form(),
            request.headers.get('X-Twilio-Signature', '')
        ):
            logger.warning(f"Invalid Twilio signature for status update {CallSid}")
            if not request.app.state.settings.is_development:
                raise HTTPException(status_code=403, detail="Invalid signature")

        # Find or create call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()

        if not call_log:
            # Create new record if it doesn't exist
            call_log = CallLog(
                call_sid=CallSid,
                direction=Direction or "outbound",
                from_number=From or "",
                to_number=To or "",
                status=CallStatus
            )
            db.add(call_log)
        else:
            # Update existing record
            call_log.status = CallStatus
            call_log.updated_at = datetime.utcnow()

        # Update timestamps based on status
        if CallStatus == "in-progress" and not call_log.start_time:
            call_log.start_time = datetime.utcnow()

        if CallStatus in ["completed", "busy", "failed", "no-answer"]:
            if not call_log.end_time:
                call_log.end_time = datetime.utcnow()

            # Set duration if provided
            if CallDuration:
                call_log.duration = int(CallDuration)
            elif Duration:
                call_log.duration = int(Duration)

        # Add recording URL if available
        if RecordingUrl:
            call_log.recording_url = RecordingUrl

        db.commit()
        db.refresh(call_log)

        # Broadcast call status event to WebSocket clients
        event_type = f"call.{CallStatus.replace('-', '_')}"
        await websocket_manager.broadcast_call_event(
            event_type=event_type,
            call_sid=CallSid,
            status=CallStatus,
            direction=call_log.direction,
            from_number=call_log.from_number,
            to_number=call_log.to_number,
            duration=call_log.duration
        )

        logger.info(f"Updated call {CallSid} status to {CallStatus}")

        return {"status": "success", "call_sid": CallSid}

    except Exception as e:
        logger.error(f"Error handling status update for {CallSid}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/outbound-twiml")
async def outbound_call_twiml(
    request: Request,
    CallSid: str = Form(...),
    To: str = Form(None)
):
    """
    Generate TwiML for outbound calls from browser.

    This is called when a browser-initiated call connects to provide
    instructions on dialing the destination phone number.
    """
    try:
        logger.info(f"Outbound TwiML requested for call {CallSid}, dialing to: {To}")

        # Generate TwiML to dial the destination number
        twiml = twilio_service.generate_outbound_twiml(to_number=To)

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error generating outbound TwiML for {CallSid}: {str(e)}")
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred.</Say></Response>'
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/voice/dial-status")
async def handle_dial_status(
    request: Request,
    CallSid: str = Form(...),
    DialCallStatus: str = Form(...),
    DialCallDuration: Optional[str] = Form(None)
):
    """
    Handle status updates for <Dial> verb.

    This is called when a forwarded/dialed call completes.
    """
    try:
        logger.info(f"Dial status for {CallSid}: {DialCallStatus}")

        # You can add additional logic here if needed
        # For now, just log it

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling dial status for {CallSid}: {str(e)}")
        return {"status": "error", "detail": str(e)}
