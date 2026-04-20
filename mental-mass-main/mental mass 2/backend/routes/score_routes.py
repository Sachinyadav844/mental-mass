"""
Mood score calculation routes
Handles POST /calculate_score endpoint
"""
from flask import Blueprint, request
from utils.error_handler import error_response, success_response, ValidationError, MLModelError
from utils.logger import log_access, log_error
from ml.score_calculator import calculate_mood_score

score_bp = Blueprint('score', __name__)


@score_bp.route('/calculate_score', methods=['POST'])
def calculate_score():
    """
    Calculate mood score from emotion, sentiment, and self-score
    
    Input:
        {
            "emotion": "sad",
            "sentiment": "negative",
            "self_score": 3  (optional, 0-10)
        }
    
    Returns:
        {
            score: float (0-10),
            risk_level: string,
            risk_color: string,
            breakdown: dict,
            emotion_score: float,
            sentiment_score: float,
            self_score: float
        }
    """
    try:
        log_access('/calculate_score', 'POST')
        
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
        
        raw_emotion = data.get("emotion")
        raw_sentiment = data.get("sentiment")
        # Safe defaults when Monitor sends null/empty after partial analysis
        emotion = (raw_emotion if isinstance(raw_emotion, str) else "") or "neutral"
        emotion = emotion.strip() or "neutral"
        sentiment = (raw_sentiment if isinstance(raw_sentiment, str) else "") or "neutral"
        sentiment = sentiment.strip() or "neutral"
        self_score = data.get('self_score')
        
        # =====================================================================
        # CALCULATE SCORE
        # =====================================================================
        try:
            result = calculate_mood_score(emotion, sentiment, self_score)
        except (ValidationError, MLModelError) as e:
            print(f"Error details: {e}")
            return error_response(e)
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        response_data = {
            'score': result['score'],
            'risk_level': result['risk_level'],
            'risk_color': result['risk_color'],
            'breakdown': result['breakdown'],
            'emotion_score': result['emotion_score'],
            'sentiment_score': result['sentiment_score'],
            'self_score': result['self_score']
        }
        
        return success_response(response_data)
    
    except Exception as e:
        print(f"Error details: {e}")
        log_error('SCORE_CALC_ERROR', str(e))
        return error_response(MLModelError(f'Score calculation error: {str(e)}'), 500)
