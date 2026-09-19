"""Custom exceptions and DRF exception handler."""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class DatasetError(Exception):
    """Base exception for dataset operations."""

    def __init__(self, message, code='dataset_error'):
        self.message = message
        self.code = code
        super().__init__(message)


class FileValidationError(DatasetError):
    """Raised when uploaded file fails validation."""

    def __init__(self, message):
        super().__init__(message, code='file_validation_error')


class AnalysisError(DatasetError):
    """Raised during dataset analysis."""

    def __init__(self, message):
        super().__init__(message, code='analysis_error')


class CleaningError(DatasetError):
    """Raised during cleaning operations."""

    def __init__(self, message):
        super().__init__(message, code='cleaning_error')


def custom_exception_handler(exc, context):
    """Handle custom exceptions and log unhandled errors."""
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'success': False,
            'error': response.data,
        }
        return response

    if isinstance(exc, DatasetError):
        logger.warning('Dataset error: %s', exc.message)
        return Response(
            {'success': False, 'error': {'message': exc.message, 'code': exc.code}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    logger.exception('Unhandled exception in API view')
    return Response(
        {'success': False, 'error': {'message': 'An unexpected error occurred.', 'code': 'server_error'}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
