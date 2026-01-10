"""
Custom Exception Handler for DRF

Provides consistent error responses across the API.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    
    Returns consistent error format:
    {
        "error": "Error type",
        "detail": "Error details",
        "error_code": "ERROR_CODE"
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = {
            'error': exc.__class__.__name__,
            'detail': str(exc),
            'error_code': getattr(exc, 'default_code', 'error').upper()
        }
        
        response.data = custom_response_data
    else:
        # Handle unexpected exceptions
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        custom_response_data = {
            'error': 'InternalServerError',
            'detail': 'An unexpected error occurred. Please try again later.',
            'error_code': 'INTERNAL_SERVER_ERROR'
        }
        
        response = Response(
            custom_response_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
