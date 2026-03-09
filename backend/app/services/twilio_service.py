from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from typing import Optional, Dict, Any
from ..config import settings
from ..utils.logger import logger


class TwilioService:
    """Service class for Twilio API operations."""

    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number
        logger.info("Twilio service initialized")

    def make_outbound_call(
        self,
        to_number: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call.

        Args:
            to_number: Destination phone number (E.164 format)
            from_number: Source phone number (defaults to configured Twilio number)

        Returns:
            Dictionary with call details including call_sid

        Raises:
            Exception: If call creation fails
        """
        try:
            if from_number is None:
                from_number = self.from_number

            # Status callback URL for real-time updates
            status_callback_url = f"{settings.webhook_base_url}/webhooks/voice/status"

            # Create the call
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=f"{settings.webhook_base_url}/webhooks/voice/outbound-twiml",
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST'
            )

            logger.info(f"Outbound call created: {call.sid} from {from_number} to {to_number}")

            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": "outbound",
                "from_number": from_number,
                "to_number": to_number,
                "date_created": call.date_created.isoformat() if call.date_created else None
            }

        except Exception as e:
            logger.error(f"Failed to create outbound call to {to_number}: {str(e)}")
            raise

    def get_call_details(self, call_sid: str) -> Dict[str, Any]:
        """
        Fetch call details from Twilio.

        Args:
            call_sid: Twilio call SID

        Returns:
            Dictionary with call details

        Raises:
            Exception: If fetching call details fails
        """
        try:
            call = self.client.calls(call_sid).fetch()

            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from_number": call.from_formatted or call.from_,
                "to_number": call.to_formatted or call.to,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "price": float(call.price) if call.price else None,
                "price_unit": call.price_unit
            }

        except Exception as e:
            logger.error(f"Failed to fetch call details for {call_sid}: {str(e)}")
            raise

    def generate_outbound_twiml(self, to_number: Optional[str] = None) -> str:
        """
        Generate TwiML for outbound calls from browser.

        Args:
            to_number: Phone number to dial (required for browser calls)

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        if to_number:
            # Dial the destination number with caller ID
            dial = Dial(caller_id=self.from_number)
            dial.number(to_number)
            response.append(dial)
            logger.info(f"Generated TwiML to dial {to_number} with caller ID {self.from_number}")
        else:
            # No number provided - play error message
            response.say("No destination number provided. Please try again.", voice='alice')
            logger.warning("TwiML requested without destination number")

        return str(response)

    def generate_incoming_twiml(
        self,
        forward_to: Optional[str] = None,
        message: Optional[str] = None
    ) -> str:
        """
        Generate TwiML for incoming calls.

        Args:
            forward_to: Phone number to forward the call to
            message: Custom message to play to the caller

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        # Play a greeting message
        greeting = message or "Thank you for calling. Please hold while we connect you."
        response.say(greeting, voice='alice')

        if forward_to:
            # Forward the call to a specific number
            dial = Dial(
                timeout=20,
                action=f"{settings.webhook_base_url}/webhooks/voice/dial-status"
            )
            dial.number(
                forward_to,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback=f"{settings.webhook_base_url}/webhooks/voice/status",
                status_callback_method='POST'
            )
            response.append(dial)
        else:
            # No forwarding number - just play a message
            response.say(
                "We are currently unable to take your call. Please try again later.",
                voice='alice'
            )

        return str(response)

    def hangup_call(self, call_sid: str) -> bool:
        """
        Terminate an active call.

        Args:
            call_sid: Twilio call SID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} terminated")
            return True

        except Exception as e:
            logger.error(f"Failed to terminate call {call_sid}: {str(e)}")
            return False

    def generate_access_token(self, identity: str, ttl: int = 3600) -> str:
        """
        Generate an access token for browser-based calling using Twilio Voice SDK.

        Args:
            identity: Unique identifier for the user/client
            ttl: Token time-to-live in seconds (default: 3600 = 1 hour)

        Returns:
            JWT access token string

        Raises:
            Exception: If token generation fails
        """
        try:
            # Create access token with credentials
            # AccessToken(account_sid, signing_key_sid, secret, identity, ttl)
            # When using Account SID/Auth Token (not API keys), use account_sid as signing_key_sid
            token = AccessToken(
                settings.twilio_account_sid,
                settings.twilio_account_sid,  # signing_key_sid (use account_sid when not using API keys)
                settings.twilio_auth_token,   # secret
                identity=identity,
                ttl=ttl
            )

            # Create a Voice grant and add to token
            voice_grant = VoiceGrant(
                outgoing_application_sid=None,  # Will use webhook URLs from REST API call
                incoming_allow=True  # Allow incoming calls
            )
            token.add_grant(voice_grant)

            # Generate the JWT token
            jwt_token = token.to_jwt()

            logger.info(f"Generated access token for identity: {identity}")
            return jwt_token

        except Exception as e:
            logger.error(f"Failed to generate access token for {identity}: {str(e)}")
            raise


# Global instance
twilio_service = TwilioService()
