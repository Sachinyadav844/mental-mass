"""
Chatbot routes
Handles POST /chatbot endpoint
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.error_handler import error_response, ValidationError, MLModelError
from utils.logger import log_access, log_error
from config import CHATBOT_MAX_HISTORY, CHATBOT_OFF_TOPIC_KEYWORDS
from database import get_user_sessions
from ml.ai_config import gemini_model
import uuid
import os
import time
from collections import defaultdict

# Rate limiting storage (in production, use Redis)
rate_limit_store = defaultdict(list)

CHATBOT_RATE_LIMIT = 1  # requests per second per user

chatbot_bp = Blueprint('chatbot', __name__)


def check_rate_limit(user_id):
    """Check if user has exceeded rate limit"""
    current_time = time.time()
    user_requests = rate_limit_store[user_id]

    # Remove requests older than 1 second
    user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < 1.0]

    # Check if under limit
    if len(user_requests) >= CHATBOT_RATE_LIMIT:
        return False

    # Add current request
    user_requests.append(current_time)
    return True


def is_mental_health_query(message):
    """Return True if the user message appears to ask about mental health."""
    normalized = message.lower()
    if not normalized:
        return False
    return not any(keyword in normalized for keyword in CHATBOT_OFF_TOPIC_KEYWORDS)


def generate_chatbot_response(message, user_id, history=None):
    """
    Generate chatbot response using Gemini

    Args:
        message: User message
        user_id: User ID for context
        history: Recent session history

    Returns:
        Dictionary with response
    """
    print("USER:", message)
    
    try:
        if not is_mental_health_query(message):
            reply = "I'm here to support your mental wellbeing. Could you tell me more about what you're feeling emotionally right now?"
            print("OFF_TOPIC_DETECTED: Redirecting to mental health focus")
            return {
                'reply': reply,
                'model': 'Gemini',
                'is_off_topic': True
            }

        SYSTEM_PROMPT = """You are a compassionate mental health assistant.

Your role:
- Listen and validate the person's feelings
- Provide 1-2 practical, actionable suggestions
- Use simple, warm language
- Do NOT diagnose or recommend medication
- Focus on coping strategies, self-care, and emotional support

Keep responses brief (2-3 sentences max) but meaningful."""

        full_prompt = SYSTEM_PROMPT + "\nUser: " + message
        response = gemini_model.generate_content(full_prompt)

        print("RAW RESPONSE:", response)

        reply = None
        if hasattr(response, "text") and response.text:
            reply = response.text.strip()
        
        if not reply:
            # Only use fallback if response was actually empty
            reply = "I hear you. What's one thing that usually helps you feel a bit better when you're going through this?"
            print("EMPTY_RESPONSE: Using fallback")

        return {
            'reply': reply,
            'model': 'Gemini',
            'is_off_topic': False
        }
    except Exception as e:
        print("Chatbot error:", str(e))
        # Vary fallback based on error type
        fallback_responses = [
            "I'm here to listen. Can you tell me what's been on your mind?",
            "It sounds like you're dealing with something difficult. I'd like to help if I can. What's happening?",
            "I'm here for you. What's troubling you right now?"
        ]
        import hashlib
        # Use message hash to pick a consistent but varied fallback
        idx = int(hashlib.md5(message.encode()).hexdigest(), 16) % len(fallback_responses)
        reply = fallback_responses[idx]
        print("EXCEPTION_FALLBACK:", reply)
        return {
            'reply': reply,
            'model': 'Gemini_Fallback',
            'is_off_topic': False
        }


@chatbot_bp.route('/chatbot', methods=['POST'])
@jwt_required()
def chatbot():
    """
    AI chatbot for mental wellness support
    
    Input:
        {
            "message": "I feel anxious",
            "session_id": "abc123" (optional)
        }
    
    Returns:
        {
            reply: string,
            session_id: string,
            turn_count: int,
            model: string
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access('/chatbot', 'POST', user_id)

        # Rate limiting check
        if not check_rate_limit(user_id):
            return error_response(
                ValidationError('Rate limit exceeded. Please wait before sending another message.'),
                429
            )

        # Safe logging (no sensitive data)
        print(f"[CHATBOT] Request from user {user_id[:8]}...")

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
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))

        print("User input:", message)
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not message:
            return jsonify({
                "success": False,
                "message": "No input provided"
            }), 400
        
        if len(message) > 1000:
            return error_response(
                ValidationError('Message exceeds maximum length of 1000 characters')
            )
        
        # =====================================================================
        # GET CONVERSATION HISTORY
        # =====================================================================
        try:
            user_sessions = get_user_sessions(user_id, limit=CHATBOT_MAX_HISTORY)
            turn_count = len(user_sessions) + 1
        except Exception:
            turn_count = 1
        
        # =====================================================================
        # GENERATE RESPONSE
        # =====================================================================
        try:
            response_data = generate_chatbot_response(
                message,
                user_id,
                history=user_sessions if 'user_sessions' in locals() else None
            )
        except MLModelError as e:
            return error_response(e)
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        return jsonify({
            'success': True,
            'data': {
                'reply': response_data.get('reply'),
                'session_id': session_id,
                'turn_count': turn_count,
                'model': response_data.get('model', 'Gemini'),
                'is_off_topic': response_data.get('is_off_topic', False)
            }
        }), 200
    
    except Exception as e:
        log_error('CHATBOT_ERROR', str(e))
        return error_response(
            MLModelError(f'Chatbot error: {str(e)}'),
            500
        )
