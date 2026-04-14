"""
Chatbot routes
Handles POST /chatbot endpoint
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.error_handler import error_response, success_response, ValidationError, MLModelError
from utils.logger import log_access, log_error
from config import (
    CHATBOT_MAX_HISTORY,
    CHATBOT_SYSTEM_PROMPT,
    CHATBOT_OFF_TOPIC_KEYWORDS,
    GEMINI_MODEL,
)
from database import get_user_sessions
from ml.ai_config import chatbot_available, gemini_model
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


def generate_chatbot_response(message, user_id, history=None):
    """
    Generate chatbot response using Gemini with ChatGPT fallback

    Args:
        message: User message
        user_id: User ID for context
        history: Recent session history

    Returns:
        Dictionary with response
    """
    try:
        # Strict system prompt for mental health only
        SYSTEM_PROMPT = """
You are a mental health assistant.
Answer only about stress, anxiety, mood, emotions.
If user asks anything else, politely refuse.
Give short, helpful responses.
"""

        # Try Gemini first
        if chatbot_available and gemini_model:
            try:
                response = gemini_model.generate_content(
                    SYSTEM_PROMPT + "\nUser: " + message
                )

                reply = response.text.strip()

                if not reply:
                    reply = "I'm here to help with your mental health. Can you tell me how you're feeling?"

                return {
                    'reply': reply,
                    'model': 'Gemini',
                    'is_off_topic': False
                }
            except Exception as e:
                print(f"[CHATBOT] Gemini failed: {e}")

        # Fallback to OpenAI ChatGPT
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if openai.api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                reply = response.choices[0].message.content.strip()
                return {
                    'reply': reply,
                    'model': 'ChatGPT',
                    'is_off_topic': False
                }
        except Exception as e:
            print(f"[CHATBOT] ChatGPT failed: {e}")

        # Final fallback
        return {
            'reply': "I'm here to help with your mental health concerns. I understand you're feeling stressed - that's completely valid. Would you like to talk about what's causing your stress or share more about how you're feeling?",
            'model': 'fallback',
            'note': 'Using mental health focused fallback response'
        }

    except Exception as e:
        print(f"[CHATBOT] Error: {str(e)}")
        return {
            'reply': 'I apologize, but I encountered an error. Please try again.',
            'model': 'error',
            'error': str(e)
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
