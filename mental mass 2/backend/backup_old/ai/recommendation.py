import random
import datetime

BASE_RECOMMENDATIONS = {
    'low': [
        {'title': 'Nature Break', 'description': 'Step outside for a short walk and breathe fresh air to reduce tension.', 'type': 'outdoor'},
        {'title': 'Guided Breathing', 'description': 'Try a 5-minute box breathing exercise to calm your nervous system.', 'type': 'breathing'},
        {'title': 'Gentle Stretching', 'description': 'Do some light stretching to release physical tension and improve mood.', 'type': 'physical'}
    ],
    'medium': [
        {'title': 'Mindfulness Journal', 'description': 'Write down your thoughts for 10 minutes to process your emotions.', 'type': 'reflection'},
        {'title': 'Creative Expression', 'description': 'Sketch, journal, or listen to soothing music to shift your mindset.', 'type': 'creative'},
        {'title': 'Connect with Someone', 'description': 'Reach out to a friend or family member for a positive conversation.', 'type': 'social'}
    ],
    'high': [
        {'title': 'Rest and Recovery', 'description': 'Take time to relax and prioritize sleep to restore emotional balance.', 'type': 'rest'},
        {'title': 'Professional Support', 'description': 'Consider talking to a mental health professional for guidance.', 'type': 'professional'},
        {'title': 'Calm Space', 'description': 'Create a quiet space and practice gentle breathing or meditation.', 'type': 'mindfulness'}
    ]
}

TIME_BASED = {
    'morning': {
        'stress': 'Start your day with a calming routine like gentle stretching and deep breathing.',
        'sad': 'Begin with gratitude: note one thing you appreciate about the new day.',
        'anxious': 'Set a small, achievable goal for the morning to build confidence.'
    },
    'afternoon': {
        'stress': 'Take a mindful break: step away from screens and practice grounding exercises.',
        'sad': 'Try a short walk in nature or listen to uplifting music.',
        'anxious': 'Focus on one task at a time with gentle breathing between activities.'
    },
    'evening': {
        'stress': 'Wind down with a relaxing routine: dim lights, herbal tea, and gentle stretching.',
        'sad': 'Reflect on positive moments from today and prepare for restorative sleep.',
        'anxious': 'Create a calming bedtime ritual with deep breathing and positive visualization.'
    }
}

EMOTION_TAGS = {
    'sad': 'Try a self-compassion exercise like noting three things that felt okay today.',
    'angry': 'Practice gentle breathing and allow some time to cool down before reacting.',
    'fear': 'Remind yourself of a small achievement and focus on one safe action.',
    'disgust': 'Choose a calming sensory activity such as soft music or a warm drink.',
    'happy': 'Keep the positive momentum by celebrating something small and steady.',
    'surprised': 'Reflect on what changed and take a few deep breaths to stay grounded.',
    'neutral': 'A simple mindful check-in can help clarify how you really feel.',
    'uncertain': 'Take a moment to breathe and notice what your body is telling you.'
}


def _time_period(hour):
    if hour is None:
        return 'afternoon'
    if 5 <= hour < 12:
        return 'morning'
    if 12 <= hour < 18:
        return 'afternoon'
    return 'evening'


def _get_emotion_category(emotion):
    """Categorize emotion for better recommendations"""
    stress_emotions = ['angry', 'fear', 'disgust']
    low_mood_emotions = ['sad', 'neutral']
    positive_emotions = ['happy', 'surprised']

    if emotion in stress_emotions:
        return 'stress'
    elif emotion in low_mood_emotions:
        return 'sad' if emotion == 'sad' else 'neutral'
    elif emotion in positive_emotions:
        return 'happy'
    return 'neutral'


def get_recommendation(score=None, emotion=None, sentiment=None, time_of_day=None, history=None):
    try:
        if score is None and history:
            scores = [session.get('score', 50) for session in history if isinstance(session.get('score', None), (int, float))]
            score = int(sum(scores) / len(scores)) if scores else 50

        if emotion is None and history:
            emotion = history[-1].get('emotion', 'neutral') if history else 'neutral'

        if sentiment is None and history:
            sentiment = history[-1].get('sentiment', 'neutral') if history else 'neutral'

        period = _time_period(time_of_day)
        emotion_category = _get_emotion_category(str(emotion).lower())

        recommendation_list = BASE_RECOMMENDATIONS['medium']
        label = 'Balanced Support'

        if score is None:
            score = 50

        if score < 35:
            recommendation_list = BASE_RECOMMENDATIONS['high']
            label = 'High Support Needed'
        elif score <= 60:
            recommendation_list = BASE_RECOMMENDATIONS['medium']
            label = 'Moderate Support'
        else:
            recommendation_list = BASE_RECOMMENDATIONS['low']
            label = 'Low Support'

        # Select 2-3 recommendations based on context
        num_recs = 3 if score < 50 else 2
        suggestions = random.sample(recommendation_list, min(num_recs, len(recommendation_list)))

        # Build personalized summary
        time_advice = TIME_BASED.get(period, {}).get(emotion_category, TIME_BASED[period]['stress'])
        emotion_advice = EMOTION_TAGS.get(str(emotion).lower(), EMOTION_TAGS['neutral'])

        summary = f"Based on your current mood score of {score}, we recommend {label.lower()}. {time_advice} {emotion_advice}"

        # Add trend analysis if history available
        if history and len(history) >= 3:
            recent_scores = [h.get('score', 50) for h in history[-3:]]
            trend = 'stable'
            if recent_scores[-1] > recent_scores[0] + 5:
                trend = 'improving'
            elif recent_scores[-1] < recent_scores[0] - 5:
                trend = 'declining'

            if trend != 'stable':
                summary += f" Your recent trend shows {trend} patterns."

        structured = {
            'text': summary,
            'score': score,
            'label': label,
            'time': period,
            'emotion': emotion,
            'sentiment': sentiment,
            'emotion_category': emotion_category,
            'suggestions': suggestions,
            'trend': trend if 'trend' in locals() else 'unknown'
        }

        return structured
    except Exception as e:
        raise ValueError(f"Recommendation generation failed: {str(e)}")


def get_recommendations_list(score=None):
    """Return multiple recommendations"""
    try:
        if score is None:
            score = 50

        if score < 35:
            return [item['title'] for item in BASE_RECOMMENDATIONS['high']]
        elif score <= 60:
            return [item['title'] for item in BASE_RECOMMENDATIONS['medium']]
        return [item['title'] for item in BASE_RECOMMENDATIONS['low']]
    except Exception as e:
        raise ValueError(f"Recommendations list generation failed: {str(e)}")
