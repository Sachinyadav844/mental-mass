"""
Chatbot routes
Handles POST /chatbot endpoint
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from utils.error_handler import error_response, success_response, ValidationError, MLModelError
from utils.logger import log_access, log_error
from config import (
    CHATBOT_MAX_HISTORY,
    CHATBOT_SYSTEM_PROMPT,
    CHATBOT_OFF_TOPIC_KEYWORDS,
    GEMINI_MODEL,
)
from database import get_user_sessions
import uuid

chatbot_bp = Blueprint('chatbot', __name__)

# Global chatbot model (lazy loaded)
_chatbot_model = None


def load_chatbot_model():
    """Load Gemini model"""
    global _chatbot_model
    
    if _chatbot_model is not None:
        return _chatbot_model
    
    try:
        import google.generativeai as genai
        from config import GEMINI_API_KEY
        
        genai.configure(api_key=GEMINI_API_KEY)
        _chatbot_model = genai.GenerativeModel(GEMINI_MODEL)
        print(f"[CHATBOT] Gemini model loaded: {GEMINI_MODEL}")
        return _chatbot_model
    
    except Exception as e:
        print(f"[CHATBOT] Failed to load Gemini model: {str(e)}")
        raise MLModelError(f'Failed to load chatbot model: {str(e)}')


def is_off_topic(message):
    """Check if message is off-topic (not mental health related)"""
    message_lower = message.lower()
    
    # Mental health keywords
    mental_health_keywords = [
        'stress', 'anxiety', 'depression', 'mood', 'emotion', 'mental', 'wellness',
        'sad', 'happy', 'angry', 'fear', 'worry', 'panic', 'therapy', 'counseling',
        'feeling', 'mood', 'emotional', 'psychological', 'mind', 'brain', 'health'
    ]
    
    has_mental_health = any(keyword in message_lower for keyword in mental_health_keywords)
    
    # Off-topic if no mental health keywords
    return not has_mental_health


def get_off_topic_response():
    """Get response for off-topic messages"""
    return {
        'reply': "I can only help with mental wellness topics. Please ask me about stress, anxiety, emotions, or other mental health concerns.",
        'is_off_topic': True,
        'model': 'filter'
    }


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
    try:
        # Check for off-topic message
        if is_off_topic(message):
            return get_off_topic_response()
        
        # Try to load model
        try:
            model = load_chatbot_model()
        except MLModelError:
            return {
                'reply': 'I apologize, but the chatbot service is currently unavailable. Please try again later.',
                'model': 'unavailable',
                'note': 'Model loading failed'
            }
        
        system_prompt = (
            "You are a mental health assistant. Only provide supportive, non-diagnostic "
            "guidance about stress, anxiety, mood, emotional well-being, and mental health. "
            "Do not give medical diagnoses or medication advice. Do not answer unrelated topics. "
            "If the user asks about something outside mental health, briefly redirect them to "
            "mental wellness. Return only mental health advice in your reply."
        )
        
        # Generate response using Gemini
        import google.generativeai as genai
        
        response = model.generate_content(f"{system_prompt}\n\nUser: {message}")
        
        reply = response.text.strip() if response.text else "I'm here to help with your mental wellness. How are you feeling today?"
        
        return {
            'reply': reply,
            'model': 'Gemini',
            'is_off_topic': False
        }
    
    except Exception as e:
        print(f"[CHATBOT] Error: {str(e)}")
        return {
            'reply': 'I apologize, but I encountered an error. Please try again.',
            'model': 'error',
            'error': str(e)
        }


@chatbot_bp.route('/chatbot', methods=['POST'])
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
        print('[CHATBOT] Request received', 'user_id=', user_id)
        print('[CHATBOT] request.files=', list(request.files.keys()))
        print('[CHATBOT] request.json=', request.get_json(silent=True))
        
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
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not message:
            return error_response(
                ValidationError('message field is required and cannot be empty')
            )
        
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
        return success_response({
            'reply': response_data.get('reply'),
            'session_id': session_id,
            'turn_count': turn_count,
            'model': response_data.get('model', 'distilgpt'),
            'is_off_topic': response_data.get('is_off_topic', False)
        })
    
    except Exception as e:
        log_error('CHATBOT_ERROR', str(e))
        return error_response(
            MLModelError(f'Chatbot error: {str(e)}'),
            500
        )
