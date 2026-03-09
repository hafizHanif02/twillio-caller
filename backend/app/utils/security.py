from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException, status
from typing import Dict
from ..config import settings
from ..utils.logger import logger


class TwilioSignatureValidator:
    """Validates Twilio webhook request signatures."""

    def __init__(self):
        """Initialize the request validator."""
        self.validator = RequestValidator(settings.twilio_auth_token)

    async def validate_request(
        self,
        request: Request,
        params: Dict[str, str]
    ) -> bool:
        """
        Validate that the request came from Twilio.

        Args:
            request: FastAPI request object
            params: Form parameters from the request

        Returns:
            True if valid, raises HTTPException if invalid

        Raises:
            HTTPException: If signature validation fails
        """
        # Get the X-Twilio-Signature header
        signature = request.headers.get('X-Twilio-Signature', '')

        # Get the full URL
        url = str(request.url)

        # Validate the signature
        is_valid = self.validator.validate(url, params, signature)

        if not is_valid:
            logger.warning(f"Invalid Twilio signature for request to {url}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Twilio signature"
            )

        logger.debug(f"Twilio signature validated for request to {url}")
        return True


# Global instance
twilio_validator = TwilioSignatureValidator()


async def validate_twilio_request(request: Request, form_data: Dict[str, str]):
    """
    Dependency for validating Twilio webhook requests.

    Usage in route:
        @app.post("/webhook")
        async def webhook(
            request: Request,
            form_data: dict = Depends(Form(...)),
            _: bool = Depends(validate_twilio_request)
        ):
            ...
    """
    # Skip validation in development mode (for testing)
    if settings.is_development and settings.app_env == "development":
        logger.warning("Skipping Twilio signature validation in development mode")
        return True

    return await twilio_validator.validate_request(request, form_data)
