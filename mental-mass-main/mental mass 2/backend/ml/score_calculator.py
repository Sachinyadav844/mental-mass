"""
Mood score calculation with weighted ensemble
"""
import numpy as np
from utils.error_handler import ValidationError, MLModelError
from config import (
    MOOD_SCORE_WEIGHTS,
    EMOTION_NUMERIC_MAP,
    SENTIMENT_NUMERIC_MAP,
    RISK_THRESHOLDS,
    RISK_COLORS
)


def calculate_mood_score(emotion, sentiment, self_score=None):
    """
    Calculate final mood score using weighted ensemble
    
    Weights:
        - facial_emotion: 60%
        - text_sentiment: 40%
        - user_self_score: 0% (removed for accuracy)
    
    Emotion mapping:
        happy → 85, neutral → 55, sad → 25, angry → 20, fear → 30
    
    Args:
        emotion: Emotion string (e.g., 'happy', 'sad')
        sentiment: Sentiment string ('positive', 'negative', 'neutral')
        self_score: User's self-reported score (ignored for accuracy)
    
    Returns:
        Dictionary with scores and risk assessment
    
    Raises:
        ValidationError
    """
    try:
        # Validate inputs
        if not emotion or not isinstance(emotion, str):
            raise ValidationError('Emotion must be a non-empty string')
        
        if not sentiment or not isinstance(sentiment, str):
            raise ValidationError('Sentiment must be a non-empty string')
        
        emotion_score = EMOTION_NUMERIC_MAP.get(emotion.lower(), 60)

        sentiment_score = SENTIMENT_NUMERIC_MAP.get(sentiment.lower(), 60)
        # Apply weights (emotion 0.6, sentiment 0.4)
        final_score = (emotion_score * 0.6) + (sentiment_score * 0.4)
        
        # Clamp final score to 0-100
        final_score = max(0, min(100, final_score))
        
        print(f"[SCORE] Emotion: {emotion} ({emotion_score}), Sentiment: {sentiment} ({sentiment_score}), Final: {final_score}")
        
        # Determine risk level
        risk_level = get_risk_level(final_score)
        risk_color = RISK_COLORS.get(risk_level, '#999999')
        
        # Breakdown
        breakdown = {
            'facial_emotion': {
                'emotion': emotion,
                'score': emotion_score,
                'weight': 0.6,
                'weighted_score': emotion_score * 0.6
            },
            'text_sentiment': {
                'sentiment': sentiment,
                'score': sentiment_score,
                'weight': 0.4,
                'weighted_score': sentiment_score * 0.4
            }
        }
        
        return {
            'score': round(final_score, 2),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'breakdown': breakdown,
            'emotion_score': emotion_score,
            'sentiment_score': sentiment_score,
            'self_score': None  # Not used
        }
    
    except ValidationError:
        raise
    except Exception as e:
        print(f"Error details: {e}")
        raise MLModelError(f'Score calculation failed: {str(e)}')


def get_risk_level(score):
    """
    Determine risk level from score (0-100 scale)
    
    Risk levels:
        - High Risk: score < 35
        - Moderate Risk: 35 <= score < 60
        - Low Risk: score >= 60
    
    Args:
        score: Numeric mood score (0-100)
    
    Returns:
        Risk level string
    """
    try:
        score = float(score)
        
        if score < 35:
            return 'High Risk'
        elif score < 60:
            return 'Moderate Risk'
        else:
            return 'Low Risk'
    
    except Exception:
        return 'Moderate Risk'


def get_risk_color(risk_level):
    """
    Get color for risk level
    
    Args:
        risk_level: Risk level string
    
    Returns:
        Color hex code
    """
    return RISK_COLORS.get(risk_level, '#999999')


def should_show_emergency_resources(risk_level):
    """
    Determine if emergency resources should be shown
    
    Args:
        risk_level: Risk level string
    
    Returns:
        Boolean
    """
    return risk_level == 'High Risk'


def smooth_score_with_history(current_score, history=[]):
    """
    Smooth score using exponential moving average of recent history
    
    Args:
        current_score: Current mood score
        history: List of recent scores (up to last 5)
    
    Returns:
        Smoothed score
    """
    try:
        if not history:
            return current_score
        
        # Use last 5 scores
        recent = history[-5:] if len(history) > 5 else history
        
        if len(recent) < 3:
            # Not enough history
            return current_score
        
        # Exponential moving average weights
        n = len(recent)
        weights = np.exp(np.linspace(-1, 0, n))
        weights = weights / weights.sum()
        
        # Add current score with highest weight
        scores = list(recent) + [current_score]
        weights_all = np.concatenate([weights * 0.5, [0.5]])
        
        smoothed = np.sum(np.array(scores) * weights_all)
        
        return round(smoothed, 2)
    
    except Exception:
        return current_score


def calculate_trend(score_history, window=7):
    """
    Calculate scoring trend (improving/declining/stable)
    
    Args:
        score_history: List of historical scores
        window: Number of recent scores to analyze
    
    Returns:
        Dictionary with trend info
    """
    try:
        if not score_history or len(score_history) < 2:
            return {'trend': 'insufficient_data', 'direction': None, 'magnitude': 0}
        
        # Get recent scores
        recent = score_history[-window:] if len(score_history) > window else score_history
        
        # Calculate change
        first = recent[0]
        last = recent[-1]
        change = last - first
        
        # Determine trend
        if change > 1:
            trend = 'improving'
            direction = 'up'
        elif change < -1:
            trend = 'declining'
            direction = 'down'
        else:
            trend = 'stable'
            direction = 'horizontal'
        
        return {
            'trend': trend,
            'direction': direction,
            'magnitude': abs(change),
            'change': round(change, 2),
            'period': len(recent),
            'first_score': first,
            'last_score': last
        }
    
    except Exception:
        return {'trend': 'error', 'direction': None, 'magnitude': 0}
