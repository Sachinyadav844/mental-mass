"""
Assessment (self-assessment questionnaire) routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.error_handler import error_response, success_response, ValidationError, DatabaseError
from utils.logger import log_access, log_error
from database import save_assessment
from config import ASSESSMENT_QUESTIONS
import uuid
import json
from datetime import datetime

assessment_bp = Blueprint('assessment', __name__)


def calculate_assessment_score(answers):
    """
    Calculate GAD-7/PHQ-9 style assessment score
    
    Args:
        answers: List of scores (0-3 per question)
    
    Returns:
        Dictionary with score and risk level
    """
    try:
        if not answers or not isinstance(answers, list):
            raise ValidationError('Answers must be a non-empty list')
        
        # Each question scored 0-3
        total = sum(answers)
        
        # Determine risk level based on total
        if total <= 4:
            risk_level = 'Low'
            description = 'Minimal anxiety/depression symptoms'
        elif total <= 9:
            risk_level = 'Mild'
            description = 'Mild anxiety/depression symptoms'
        elif total <= 14:
            risk_level = 'Moderate'
            description = 'Moderate anxiety/depression symptoms'
        elif total <= 19:
            risk_level = 'Moderately Severe'
            description = 'Moderately severe anxiety/depression symptoms'
        else:
            risk_level = 'Severe'
            description = 'Severe anxiety/depression symptoms'
        
        return {
            'total_score': total,
            'max_score': len(answers) * 3,
            'risk_level': risk_level,
            'description': description
        }
    
    except ValidationError:
        raise
    except Exception as e:
        raise DatabaseError(f'Failed to calculate assessment score: {str(e)}')


@assessment_bp.route('/assessment/questions', methods=['GET'])
@jwt_required()
def get_assessment_questions():
    """Get assessment questionnaire questions"""
    try:
        log_access('/assessment/questions', 'GET', get_jwt_identity())
        
        return success_response({
            'questions': ASSESSMENT_QUESTIONS,
            'total_questions': len(ASSESSMENT_QUESTIONS),
            'scale': 'Likert (0-3)'
        })
    
    except Exception as e:
        log_error('ASSESSMENT_QUESTIONS_ERROR', str(e))
        return error_response(
            DatabaseError(f'Failed to fetch questions: {str(e)}'),
            500
        )


@assessment_bp.route('/assessment', methods=['POST'])
@jwt_required()
def submit_assessment():
    """
    Submit self-assessment responses
    
    Input:
        {
            "answers": [3, 2, 4, 1, 3]  (array of scores 0-3)
        }
    
    Returns:
        {
            assessment_id: string,
            total_score: int,
            risk_level: string,
            description: string,
            recommendations: list
        }
    """
    try:
        user_id = get_jwt_identity()
        log_access('/assessment', 'POST', user_id)
        
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
        
        answers = data.get('answers', [])
        
        # =====================================================================
        # VALIDATE ANSWERS
        # =====================================================================
        if not answers or not isinstance(answers, list):
            return error_response(
                ValidationError('answers must be a non-empty array')
            )
        
        if len(answers) != len(ASSESSMENT_QUESTIONS):
            return error_response(
                ValidationError(f'Expected {len(ASSESSMENT_QUESTIONS)} answers, got {len(answers)}')
            )
        
        # Validate each answer is 0-3
        try:
            answers_int = [int(a) for a in answers]
            if any(a < 0 or a > 3 for a in answers_int):
                return error_response(
                    ValidationError('Each answer must be between 0 and 3')
                )
            answers = answers_int
        except (ValueError, TypeError):
            return error_response(
                ValidationError('Each answer must be a number')
            )
        
        # =====================================================================
        # CALCULATE SCORE
        # =====================================================================
        try:
            score_result = calculate_assessment_score(answers)
        except (ValidationError, DatabaseError) as e:
            return error_response(e)
        
        # =====================================================================
        # GENERATE RECOMMENDATIONS
        # =====================================================================
        recommendations = _get_assessment_recommendations(score_result['risk_level'])
        
        # =====================================================================
        # SAVE ASSESSMENT
        # =====================================================================
        try:
            assessment_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'answers': json.dumps(answers),
                'total_score': score_result['total_score'],
                'risk_level': score_result['risk_level']
            }
            
            db_assessment = save_assessment(assessment_data)
        
        except Exception as e:
            log_error('ASSESSMENT_SAVE_ERROR', str(e), str(e))
            return error_response(
                DatabaseError(f'Failed to save assessment: {str(e)}'),
                500
            )
        
        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        response_data = {
            'assessment_id': db_assessment.id,
            'total_score': score_result['total_score'],
            'max_score': score_result['max_score'],
            'risk_level': score_result['risk_level'],
            'description': score_result['description'],
            'recommendations': recommendations,
            'timestamp': db_assessment.timestamp.isoformat()
        }
        
        return success_response(response_data, 201)
    
    except Exception as e:
        log_error('ASSESSMENT_ERROR', str(e))
        return error_response(
            DatabaseError(f'Assessment error: {str(e)}'),
            500
        )


def _get_assessment_recommendations(risk_level):
    """Get recommendations based on assessment risk level"""
    
    recommendations_map = {
        'Low': [
            'Keep up your wellness routine',
            'Maintain regular exercise and healthy habits',
            'Continue practicing stress management techniques',
            'Schedule regular check-ins with your mental health provider'
        ],
        'Mild': [
            'Consider scheduling an appointment with a therapist',
            'Practice daily relaxation techniques (meditation, yoga)',
            'Increase physical activity (30 minutes daily)',
            'Maintain a consistent sleep schedule'
        ],
        'Moderate': [
            'Schedule an appointment with a mental health professional',
            'Implement daily self-care routines',
            'Consider cognitive-behavioral therapy (CBT)',
            'Reach out to supportive friends or family',
            'Limit caffeine and alcohol consumption'
        ],
        'Moderately Severe': [
            'Contact your doctor or mental health professional urgently',
            'Consider therapy sessions 1-2 times per week',
            'Explore medication options with a healthcare provider',
            'Build a strong support network',
            'Consider crisis resources if needed'
        ],
        'Severe': [
            'Contact a mental health professional immediately',
            'Consider psychiatric evaluation and medication',
            'If in crisis, call 988 (US Suicide & Crisis Lifeline)',
            'Consider hospitalization or intensive outpatient programs',
            'Activate your emergency support network'
        ]
    }
    
    return recommendations_map.get(risk_level, [])
