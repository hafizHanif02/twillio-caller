from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models import CallLog
from ..services.twilio_service import twilio_service
from ..services.websocket_manager import websocket_manager
from ..utils.logger import logger


class CallService:
    """Service for managing call operations."""

    async def initiate_outbound_call(
        self,
        to_number: str,
        db: Session,
        from_number: Optional[str] = None
    ) -> CallLog:
        """
        Initiate an outbound call and create database record.

        Args:
            to_number: Destination phone number
            db: Database session
            from_number: Source phone number (optional)

        Returns:
            CallLog instance

        Raises:
            Exception: If call creation fails
        """
        try:
            # Make the call via Twilio
            call_data = twilio_service.make_outbound_call(to_number, from_number)

            # Create database record
            call_log = CallLog(
                call_sid=call_data["call_sid"],
                direction="outbound",
                from_number=call_data["from_number"],
                to_number=call_data["to_number"],
                status=call_data["status"],
                start_time=datetime.utcnow() if call_data["status"] != "queued" else None
            )

            db.add(call_log)
            db.commit()
            db.refresh(call_log)

            logger.info(f"Initiated outbound call: {call_log.call_sid}")

            # Broadcast to WebSocket clients
            await websocket_manager.broadcast_call_event(
                event_type="call.initiated",
                call_sid=call_log.call_sid,
                status=call_log.status,
                direction="outbound",
                from_number=call_log.from_number,
                to_number=call_log.to_number
            )

            return call_log

        except Exception as e:
            logger.error(f"Failed to initiate outbound call to {to_number}: {str(e)}")
            db.rollback()
            raise

    def get_call_by_sid(self, call_sid: str, db: Session) -> Optional[CallLog]:
        """
        Get a call by its Twilio SID.

        Args:
            call_sid: Twilio call SID
            db: Database session

        Returns:
            CallLog instance or None
        """
        return db.query(CallLog).filter(CallLog.call_sid == call_sid).first()

    def get_call_history(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        direction: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[CallLog], int]:
        """
        Get call history with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            direction: Filter by call direction (inbound/outbound)
            status: Filter by call status

        Returns:
            Tuple of (list of CallLog instances, total count)
        """
        query = db.query(CallLog)

        # Apply filters
        if direction:
            query = query.filter(CallLog.direction == direction)

        if status:
            query = query.filter(CallLog.status == status)

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        calls = query.order_by(desc(CallLog.created_at)).offset(skip).limit(limit).all()

        logger.debug(f"Retrieved {len(calls)} calls (total: {total})")

        return calls, total

    async def sync_call_from_twilio(self, call_sid: str, db: Session) -> CallLog:
        """
        Sync call data from Twilio API and update database.

        Args:
            call_sid: Twilio call SID
            db: Database session

        Returns:
            Updated CallLog instance

        Raises:
            Exception: If fetching call details fails
        """
        try:
            # Fetch latest data from Twilio
            call_data = twilio_service.get_call_details(call_sid)

            # Find or create call log
            call_log = self.get_call_by_sid(call_sid, db)

            if not call_log:
                # Create new record
                call_log = CallLog(
                    call_sid=call_sid,
                    direction=call_data["direction"],
                    from_number=call_data["from_number"],
                    to_number=call_data["to_number"],
                    status=call_data["status"]
                )
                db.add(call_log)
            else:
                # Update existing record
                call_log.status = call_data["status"]
                call_log.duration = call_data.get("duration")
                call_log.price = call_data.get("price")
                call_log.price_unit = call_data.get("price_unit")

            # Update timestamps
            if call_data.get("start_time"):
                call_log.start_time = datetime.fromisoformat(call_data["start_time"].replace('Z', '+00:00'))

            if call_data.get("end_time"):
                call_log.end_time = datetime.fromisoformat(call_data["end_time"].replace('Z', '+00:00'))

            db.commit()
            db.refresh(call_log)

            logger.info(f"Synced call {call_sid} from Twilio")

            return call_log

        except Exception as e:
            logger.error(f"Failed to sync call {call_sid} from Twilio: {str(e)}")
            db.rollback()
            raise

    def get_call_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get call statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with call statistics
        """
        total_calls = db.query(CallLog).count()
        inbound_calls = db.query(CallLog).filter(CallLog.direction == "inbound").count()
        outbound_calls = db.query(CallLog).filter(CallLog.direction == "outbound").count()
        completed_calls = db.query(CallLog).filter(CallLog.status == "completed").count()
        failed_calls = db.query(CallLog).filter(CallLog.status.in_(["failed", "busy", "no-answer"])).count()

        return {
            "total_calls": total_calls,
            "inbound_calls": inbound_calls,
            "outbound_calls": outbound_calls,
            "completed_calls": completed_calls,
            "failed_calls": failed_calls,
            "success_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
        }


# Global instance
call_service = CallService()
