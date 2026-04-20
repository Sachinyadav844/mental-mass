"""
Error handling and response formatting for MentalMass
"""
from flask import jsonify
from utils.logger import log_error


class MentalMassError(Exception):
    """Base exception for MentalMass"""
    def __init__(self, message, code='UNKNOWN_ERROR', status_code=500, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or ''
        super().__init__(message)


class ValidationError(MentalMassError):
    """Input validation error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'VALIDATION_ERROR', 400, details)


class NoFaceDetectedError(MentalMassError):
    """Face detection failed error"""
    def __init__(self, details=None):
        super().__init__('No face detected in image', 'NO_FACE', 400, details)


class ImageProcessingError(MentalMassError):
    """Image processing error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'IMAGE_ERROR', 422, details)


class MLModelError(MentalMassError):
    """ML model processing error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'ML_ERROR', 500, details)


class DatabaseError(MentalMassError):
    """Database operation error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'DB_ERROR', 500, details)


class AuthenticationError(MentalMassError):
    """Authentication error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'AUTH_ERROR', 401, details)


class ChatbotError(MentalMassError):
    """Chatbot processing error"""
    def __init__(self, message, details=None):
        super().__init__(message, 'CHATBOT_ERROR', 500, details)


# ============================================================================
# ERROR RESPONSE FORMATTER
# ============================================================================

def error_response(error, status_code=None):
    """Format error as JSON response"""
    if isinstance(error, MentalMassError):
        status = status_code or error.status_code
        log_error(error.code, error.message, error.details)
        payload = {
            'success': False,
            'message': error.message,
            'code': error.code,
        }
        if error.details:
            payload['details'] = error.details
        return jsonify(payload), status
    
    # Generic error
    status = status_code or 500
    log_error('INTERNAL_ERROR', str(error))
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'code': 'INTERNAL_ERROR',
        'details': str(error)
    }), status


def success_response(data, status_code=200):
    """Format success as JSON response"""
    if isinstance(data, dict):
        return jsonify({
            'success': True,
            **data
        }), status_code
    
    return jsonify({
        'success': True,
        'data': data
    }), status_code


# ============================================================================
# ERROR HANDLER (for Flask app)
# ============================================================================

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(MentalMassError)
    def handle_mentalmass_error(error):
        return error_response(error)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        return error_response(
            ValidationError('Invalid request'),
            400
        )
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        return error_response(
            AuthenticationError('Unauthorized access'),
            401
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return error_response(error, 500)
