"""
Text analysis routes
Handles POST /analyze_text endpoint
"""
from flask import Blueprint, request
from utils.error_handler import error_response, success_response, ValidationError, MLModelError
from utils.logger import log_access, log_error
from ml.sentiment_analyzer import analyze_text_sentiment

text_bp = Blueprint('text', __name__)


@text_bp.route('/analyze_text', methods=['POST'])
def analyze_text():
    """
    Analyze sentiment of text
    
    Input:
        {
            "text": "I feel terrible today"
        }
    
    Returns:
        {
            sentiment: string,
            confidence: float (0-1),
            keywords: list,
            model_used: string,
            word_count: int,
            is_short_text: bool
        }
    """
    try:
        log_access('/analyze_text', 'POST')
        print('[TEXT] Request received', 'json=', request.is_json)
        print('[TEXT] request.json=', request.get_json(silent=True))
        
        # =====================================================================
        # PARSE INPUT
        # =====================================================================
        if not request.is_json:
            return error_response(
                ValidationError('Content-Type must be application/json')
            )
        
        data = request.get_json(silent=True)
        if not data:
            return error_response(
                ValidationError('Empty request body')
            )
        
        text = data.get('text', '').strip()
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not text:
            return error_response(
                ValidationError('Text field is required and cannot be empty')
            )
        
        if len(text) > 10000:
            return error_response(
                ValidationError('Text exceeds maximum length of 10000 characters')
            )
        
        # =====================================================================
        # ANALYZE SENTIMENT
        # =====================================================================
        try:
            result = analyze_text_sentiment(text)
        except (ValidationError, MLModelError) as e:
            return error_response(e)
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        response_data = {
            'sentiment': result['sentiment'],
            'confidence': result['confidence'],
            'keywords': result['keywords'],
            'model_used': result['model_used'],
            'word_count': result['word_count'],
            'is_short_text': result['is_short_text']
        }
        
        return success_response(response_data)
    
    except Exception as e:
        log_error('TEXT_ANALYSIS_ERROR', str(e))
        return error_response(MLModelError(f'Text analysis error: {str(e)}'), 500)
