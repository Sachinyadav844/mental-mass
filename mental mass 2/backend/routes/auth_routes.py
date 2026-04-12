"""
Authentication routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from utils.error_handler import error_response, success_response, ValidationError, AuthenticationError, DatabaseError
from utils.logger import log_access, log_error
from database import create_user, get_user_by_email, get_user_by_id, init_db
import uuid
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    return True, 'OK'


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user
    
    Input:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secure_password123"
        }
    
    Returns:
        {
            user: {id, name, email},
            token: JWT token
        }
    """
    try:
        log_access('/register', 'POST')
        
        # =====================================================================
        # PARSE INPUT
        # =====================================================================
        if not request.is_json:
            return error_response(
                ValidationError('Content-Type must be application/json')
            )
        
        data = request.get_json()
        if not data:
            return error_response(
                ValidationError('Empty request body')
            )
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not name:
            return error_response(
                ValidationError('name field is required')
            )
        
        if len(name) < 2:
            return error_response(
                ValidationError('name must be at least 2 characters')
            )
        
        if not email:
            return error_response(
                ValidationError('email field is required')
            )
        
        if not validate_email(email):
            return error_response(
                ValidationError('Invalid email format')
            )
        
        if not password:
            return error_response(
                ValidationError('password field is required')
            )
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return error_response(
                ValidationError(message)
            )
        
        # =====================================================================
        # CHECK EXISTING USER
        # =====================================================================
        try:
            existing_user = get_user_by_email(email)
            if existing_user:
                return error_response(
                    ValidationError('User already exists with this email'),
                    409
                )
        except Exception as e:
            log_error('REGISTER_DB_CHECK_ERROR', str(e))
            return error_response(
                DatabaseError(f'Database error: {str(e)}'),
                500
            )
        
        # =====================================================================
        # CREATE USER
        # =====================================================================
        try:
            user_id = str(uuid.uuid4())
            user = create_user(user_id, name, email, password, firebase_auth=False)
            
            print(f"[AUTH] User registered: {email}")
        
        except Exception as e:
            log_error('REGISTER_CREATE_ERROR', str(e))
            return error_response(
                DatabaseError(f'Failed to create user: {str(e)}'),
                500
            )
        
        # =====================================================================
        # CREATE JWT TOKEN
        # =====================================================================
        token = create_access_token(identity=user.id)
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        return success_response({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            },
            'token': token
        }, 201)
    
    except Exception as e:
        log_error('REGISTER_ERROR', str(e))
        return error_response(
            DatabaseError(f'Registration error: {str(e)}'),
            500
        )


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user with email/password
    
    Input:
        {
            "email": "john@example.com",
            "password": "secure_password123"
        }
    
    Returns:
        {
            user: {id, name, email},
            token: JWT token
        }
    """
    try:
        log_access('/login', 'POST')
        
        # =====================================================================
        # PARSE INPUT
        # =====================================================================
        if not request.is_json:
            return error_response(
                ValidationError('Content-Type must be application/json')
            )
        
        data = request.get_json()
        if not data:
            return error_response(
                ValidationError('Empty request body')
            )
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not email or not password:
            return error_response(
                ValidationError('email and password are required')
            )
        
        # =====================================================================
        # FETCH USER
        # =====================================================================
        try:
            user = get_user_by_email(email)
        except Exception as e:
            log_error('LOGIN_DB_ERROR', str(e))
            return error_response(
                DatabaseError(f'Database error: {str(e)}'),
                500
            )
        
        if not user:
            return error_response(
                AuthenticationError('Invalid email or password'),
                401
            )
        
        # =====================================================================
        # VERIFY PASSWORD
        # =====================================================================
        if not user.check_password(password):
            return error_response(
                AuthenticationError('Invalid email or password'),
                401
            )
        
        # =====================================================================
        # CREATE JWT TOKEN
        # =====================================================================
        token = create_access_token(identity=user.id)
        
        print(f"[AUTH] User logged in: {email}")
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        return success_response({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            },
            'token': token
        })
    
    except Exception as e:
        log_error('LOGIN_ERROR', str(e))
        return error_response(
            DatabaseError(f'Login error: {str(e)}'),
            500
        )


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        log_access('/profile', 'GET', user_id)
        
        try:
            user = get_user_by_id(user_id)
        except Exception as e:
            log_error('PROFILE_DB_ERROR', str(e))
            return error_response(
                DatabaseError(f'Database error: {str(e)}'),
                500
            )
        
        if not user:
            return error_response(
                ValidationError('User not found'),
                404
            )
        
        return success_response({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
    
    except Exception as e:
        log_error('PROFILE_ERROR', str(e))
        return error_response(
            DatabaseError(f'Profile error: {str(e)}'),
            500
        )
