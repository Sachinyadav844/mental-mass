"""
Recommendation routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.error_handler import error_response, success_response, ValidationError, DatabaseError
from utils.logger import log_access, log_error
from database import get_user_sessions
import json

recommendation_bp = Blueprint('recommendation', __name__)

# Recommendation bank
RECOMMENDATIONS_BY_RISK = {
    'High Risk': {
        'category': 'immediate_support',
        'suggestions': [
            'Please reach out to a mental health professional immediately',
            'Contact a trusted friend or family member for support',
            'Try grounding techniques like the 5-4-3-2-1 method',
            'Consider calling a crisis helpline for immediate assistance',
            'Practice slow breathing exercises (4-7-8 technique)',
            'Go for a walk in nature if possible',
            'Engage in a calming activity or hobby'
        ],
        'emergency_resources': [
            {
                'name': 'National Suicide Prevention Lifeline',
                'phone': '1-800-273-8255',
                'available': '24/7',
                'url': 'https://suicidepreventionlifeline.org'
            },
            {
                'name': 'Crisis Text Line',
                'text': 'Text HOME to 741741',
                'available': '24/7',
                'url': 'https://www.crisistextline.org'
            },
            {
                'name': 'SAMHSA National Helpline',
                'phone': '1-800-662-4357',
                'available': '24/7',
                'url': 'https://www.samhsa.gov'
            }
        ]
    },
    'Moderate Risk': {
        'category': 'supportive_care',
        'suggestions': [
            'Schedule an appointment with a therapist or counselor',
            'Practice regular exercise and physical activity',
            'Maintain a healthy sleep schedule',
            'Try meditation or mindfulness exercises',
            'Spend time with supportive friends and family',
            'Engage in activities that bring you joy',
            'Consider journaling to express your feelings',
            'Limit caffeine and alcohol consumption'
        ],
        'emergency_resources': []
    },
    'Low Risk': {
        'category': 'wellness_maintenance',
        'suggestions': [
            'Keep up with regular exercise and healthy habits',
            'Maintain social connections and relationships',
            'Practice gratitude and positive thinking',
            'Continue your wellness routine',
            'Take time for self-care activities',
            'Stay organized and manage stress effectively',
            'Keep setting and achieving personal goals',
            'Share your experiences with others'
        ],
        'emergency_resources': []
    }
}

EMOTION_SPECIFIC_SUGGESTIONS = {
    'sad': [
        'Engage in activities that normally bring you joy',
        'Reach out to people you care about',
        'Allow yourself to feel your emotions, but don\'t dwell',
        'Try to maintain a routine and do things you enjoy'
    ],
    'angry': [
        'Take a break and practice deep breathing',
        'Go for a run or exercise to release tension',
        'Write down your feelings without judgment',
        'Try progressive muscle relaxation'
    ],
    'anxious': [
        'Practice grounding techniques (5 senses exercise)',
        'Try the Pomodoro technique for focused work',
        'Take breaks and step away from stressors',
        'Practice progressive muscle relaxation or yoga'
    ],
    'fear': [
        'Identify what specifically you\'re afraid of',
        'Break down the fear into manageable steps',
        'Practice facing fears gradually',
        'Seek support from trusted people'
    ],
    'happy': [
        'Maintain this positive energy',
        'Share your happiness with others',
        'Document this positive moment',
        'Use this momentum for positive action'
    ]
}


@recommendation_bp.route('/recommendation', methods=['POST'])
@jwt_required()
def get_recommendation():
    """
    Get personalized recommendations based on mood score, emotion, and sentiment
    
    Input:
        {
            "score": 25.5,
            "risk_level": "High Risk",
            "emotion": "sad",
            "sentiment": "negative"
        }
    
    Returns:
        {
            category: string,
            suggestions: list,
            emergency_resources: list,
            emotion_specific: list,
            sentiment_specific: list
        }
    """
    try:
        log_access('/recommendation', 'POST', get_jwt_identity())
        
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
        
        risk_level = data.get('risk_level', '').strip()
        emotion = data.get('emotion', '').strip().lower()
        sentiment = data.get('sentiment', '').strip().lower()
        
        # =====================================================================
        # VALIDATE INPUT
        # =====================================================================
        if not risk_level:
            return error_response(
                ValidationError('risk_level field is required')
            )
        
        if risk_level not in RECOMMENDATIONS_BY_RISK:
            return error_response(
                ValidationError(f'Invalid risk_level: {risk_level}')
            )
        
        # =====================================================================
        # BUILD RECOMMENDATION
        # =====================================================================
        try:
            recommendation = RECOMMENDATIONS_BY_RISK[risk_level].copy()
            
            # Add emotion-specific suggestions
            if emotion in EMOTION_SPECIFIC_SUGGESTIONS:
                recommendation['emotion_specific'] = EMOTION_SPECIFIC_SUGGESTIONS[emotion]
            else:
                recommendation['emotion_specific'] = []
            
            # Add sentiment-specific suggestions
            sentiment_suggestions = []
            if sentiment == 'negative':
                sentiment_suggestions = [
                    'Try positive affirmations daily',
                    'Practice gratitude journaling',
                    'Reach out to supportive friends',
                    'Consider professional counseling'
                ]
            elif sentiment == 'positive':
                sentiment_suggestions = [
                    'Build on this positive momentum',
                    'Share your positivity with others',
                    'Document what\'s working well',
                    'Set small achievable goals'
                ]
            else:  # neutral
                sentiment_suggestions = [
                    'Reflect on your current state',
                    'Try mindfulness meditation',
                    'Engage in light physical activity',
                    'Connect with loved ones'
                ]
            
            recommendation['sentiment_specific'] = sentiment_suggestions
            
        except Exception as e:
            log_error('RECOMMENDATION_BUILD_ERROR', str(e))
            return error_response(
                ValidationError(f'Failed to build recommendations: {str(e)}')
            )
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        return success_response(recommendation)
    
    except Exception as e:
        log_error('RECOMMENDATION_ERROR', str(e))
        return error_response(DatabaseError(f'Recommendation error: {str(e)}'), 500)


@recommendation_bp.route('/recommendations_all', methods=['GET'])
@jwt_required()
def get_all_recommendations():
    """Get all recommendation templates for reference"""
    return success_response({
        'by_risk': RECOMMENDATIONS_BY_RISK,
        'emotion_specific': EMOTION_SPECIFIC_SUGGESTIONS
    })
