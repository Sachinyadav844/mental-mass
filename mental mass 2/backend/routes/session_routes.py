"""
Session management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.error_handler import error_response, success_response, ValidationError, DatabaseError
from utils.logger import log_access, log_error
from utils.socketio_manager import emit_dashboard_update, emit_session_created
from database import (
    get_user_sessions, get_session_stats, save_session_data
)
from config import SESSIONS_LIMIT
import uuid
from datetime import datetime
import json

session_bp = Blueprint('session', __name__)


@session_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """
    Get user's recent sessions
    
    Query params:
        ?limit=30 (default 30, max 100)
    
    Returns:
        {
            sessions: list,
            total: int,
            limit: int
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access('/sessions', 'GET', user_id)
        
        # Get limit from query params
        limit = request.args.get('limit', SESSIONS_LIMIT, type=int)
        limit = min(limit, 100)  # Max 100
        
        # Fetch sessions
        sessions = get_user_sessions(user_id, limit=limit)
        
        return success_response({
            'sessions': sessions,
            'total': len(sessions),
            'limit': limit
        })
    
    except Exception as e:
        log_error('SESSIONS_FETCH_ERROR', str(e), str(e))
        return error_response(
            DatabaseError(f'Failed to fetch sessions: {str(e)}'),
            500
        )


@session_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """
    Save a new analysis session
    
    Input:
        {
            "emotion": "happy",
            "emotion_confidence": 0.87,
            "all_emotions": {...},
            "sentiment": "positive",
            "sentiment_confidence": 0.92,
            "sentiment_keywords": [...],
            "mood_score": 8.5,
            "risk_level": "Low Risk",
            "risk_color": "#22c55e",
            "face_detected": true,
            "face_box": {x: 100, y: 100, width: 50, height: 50},
            "self_score": 8,
            "image_source": "webcam"
        }
    
    Returns:
        {
            session_id: string,
            timestamp: ISO string
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access('/sessions', 'POST', user_id)
        
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
        
        # =====================================================================
        # BUILD SESSION OBJECT
        # =====================================================================
        session_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'emotion': data.get('emotion'),
            'emotion_confidence': data.get('emotion_confidence'),
            'all_emotions': json.dumps(data.get('all_emotions', {})),
            'sentiment': data.get('sentiment'),
            'sentiment_confidence': data.get('sentiment_confidence'),
            'sentiment_keywords': json.dumps(data.get('sentiment_keywords', [])),
            'mood_score': data.get('mood_score'),
            'risk_level': data.get('risk_level'),
            'risk_color': data.get('risk_color'),
            'face_detected': data.get('face_detected', False),
            'face_box': json.dumps(data.get('face_box')),
            'self_score': data.get('self_score'),
            'image_source': data.get('image_source', 'unknown')
        }
        
        # =====================================================================
        # SAVE SESSION
        # =====================================================================
        try:
            db_session = save_session_data(session_data)
            
            # Emit real-time dashboard update
            emit_dashboard_update({
                "session_id": db_session.id,
                "emotion": session_data.get('emotion'),
                "sentiment": session_data.get('sentiment'),
                "mood_score": session_data.get('mood_score'),
                "risk_level": session_data.get('risk_level'),
                "timestamp": db_session.timestamp.isoformat()
            })
            
            # Emit session created event
            emit_session_created({
                'session_id': db_session.id,
                'timestamp': db_session.timestamp.isoformat()
            })
            
            return success_response({
                'session_id': db_session.id,
                'timestamp': db_session.timestamp.isoformat()
            }, 201)
        
        except Exception as e:
            log_error('SESSION_SAVE_ERROR', str(e), str(e))
            return error_response(
                DatabaseError(f'Failed to save session: {str(e)}'),
                500
            )
    
    except Exception as e:
        log_error('SESSION_CREATE_ERROR', str(e), str(e))
        return error_response(
            DatabaseError(f'Session creation error: {str(e)}'),
            500
        )


@session_bp.route('/sessions/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Get aggregate session statistics for user
    
    Returns:
        {
            total_sessions: int,
            avg_mood_score: float,
            emotion_distribution: dict,
            risk_distribution: dict,
            last_session: dict
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access('/sessions/stats', 'GET', user_id)
        
        # Fetch stats
        stats = get_session_stats(user_id)
        
        return success_response(stats)
    
    except Exception as e:
        log_error('STATS_FETCH_ERROR', str(e), str(e))
        return error_response(
            DatabaseError(f'Failed to fetch statistics: {str(e)}'),
            500
        )


@session_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session_detail(session_id):
    """
    Get details of a specific session
    
    Returns:
        {
            session: dict (full session object)
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access(f'/sessions/{session_id}', 'GET', user_id)
        
        # Fetch sessions and find matching one
        sessions = get_user_sessions(user_id, limit=100)
        
        session = next((s for s in sessions if s['id'] == session_id), None)
        
        if not session:
            return error_response(
                ValidationError('Session not found'),
                404
            )
        
        return success_response({'session': session})
    
    except Exception as e:
        log_error('SESSION_DETAIL_ERROR', str(e), str(e))
        return error_response(
            DatabaseError(f'Failed to fetch session: {str(e)}'),
            500
        )
