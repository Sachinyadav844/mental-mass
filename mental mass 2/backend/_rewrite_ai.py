from pathlib import Path

sentiment = '''import os
import re
import random

TRANSFORMERS_AVAILABLE = False
sentiment_pipeline = None

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
NEGATIVE_KEYWORDS = [
    'sad', 'depressed', 'anxious', 'stress', 'tired', 'overwhelmed', 'upset', 'angry', 'worried', 'afraid', 'lonely'
]
POSITIVE_KEYWORDS = [
    'happy', 'good', 'better', 'relaxed', 'calm', 'grateful', 'safe', 'hopeful', 'supported', 'okay'
]


def load_transformers():
    """Lazy load transformers only when needed"""
    global TRANSFORMERS_AVAILABLE, sentiment_pipeline
    if TRANSFORMERS_AVAILABLE or sentiment_pipeline:
        return

    try:
        print("[AI] Attempting to load transformers for sentiment...")
        from transformers import pipeline
        sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME)
        TRANSFORMERS_AVAILABLE = True
        print("[AI] Sentiment model loaded successfully")
    except Exception as e:
        TRANSFORMERS_AVAILABLE = False
        print(f"[AI] Transformers not available ({e}), using rule-based sentiment")


def clean_text(text):
    if not isinstance(text, str):
        return ''
    text = text.strip()
    text = re.sub(r'https?://\\S+', '', text)
    text = re.sub(r'@\\w+', '', text)
    text = re.sub(r'[^\\w\\s\\.,!\\?]', '', text)
    text = re.sub(r'\\s+', ' ', text)
    return text.strip()


def analyze_sentiment(text):
    text = clean_text(text)
    if not text:
        return {'sentiment': 'neutral', 'score': 0.5, 'confidence': 0.5, 'keywords': ['empty']}

    load_transformers()
    sentiment = 'neutral'
    confidence = 0.5

    if TRANSFORMERS_AVAILABLE and sentiment_pipeline:
        try:
            result = sentiment_pipeline(text[:512])[0]
            label = result.get('label', '')
            confidence = float(result.get('score', 0.5))

            if label == 'LABEL_2':
                sentiment = 'positive'
            elif label == 'LABEL_0':
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            if len(text) < 40 and sentiment == 'neutral':
                confidence = min(confidence + 0.07, 0.85)

            if len(text) < 25:
                confidence = max(0.55, confidence - 0.05)

            if any(word in text.lower() for word in NEGATIVE_KEYWORDS) and sentiment == 'positive':
                sentiment = 'neutral'
                confidence = min(confidence, 0.65)
            if any(word in text.lower() for word in POSITIVE_KEYWORDS) and sentiment == 'negative':
                sentiment = 'neutral'
                confidence = min(confidence, 0.7)

        except Exception as e:
            print(f"[AI] Sentiment pipeline failed: {e}")
            sentiment, confidence = _rule_based_sentiment(text)
    else:
        sentiment, confidence = _rule_based_sentiment(text)

    keywords = extract_keywords(text)
    return {
        'sentiment': sentiment,
        'score': round(confidence, 2),
        'confidence': round(confidence, 2),
        'keywords': keywords
    }


def _rule_based_sentiment(text):
    lower = text.lower()
    negative_count = sum(lower.count(word) for word in NEGATIVE_KEYWORDS)
    positive_count = sum(lower.count(word) for word in POSITIVE_KEYWORDS)

    if negative_count > positive_count:
        sentiment = 'negative'
    elif positive_count > negative_count:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'

    confidence = 0.55 + min(abs(positive_count - negative_count) * 0.1, 0.35)
    if len(text) < 30:
        confidence = max(confidence - 0.05, 0.5)
    return sentiment, round(confidence, 2)


def extract_keywords(text):
    tokens = [token.lower().strip('.,!?') for token in text.split()]
    keywords = [token for token in tokens if token in NEGATIVE_KEYWORDS + POSITIVE_KEYWORDS]
    return keywords[:5] if keywords else ['general']
'''

scoring = '''def calculate_score_details(emotion, sentiment, history_scores=None):
    if not isinstance(emotion, str) or not isinstance(sentiment, str):
        raise ValueError('Emotion and sentiment must be strings')

    emotion = emotion.lower()
    sentiment = sentiment.lower()

    weights = {
        'emotion': {
            'happy': 24,
            'neutral': 10,
            'sad': -18,
            'angry': -28,
            'fear': -22,
            'surprise': 12,
            'disgust': -16,
            'uncertain': -5
        },
        'sentiment': {
            'positive': 35,
            'neutral': 10,
            'negative': -35
        }
    }

    emotion_score = weights['emotion'].get(emotion, 0)
    sentiment_score = weights['sentiment'].get(sentiment, 0)
    total = 50 + emotion_score + sentiment_score

    if emotion in ['sad', 'angry', 'fear', 'disgust'] and sentiment == 'negative':
        total -= 12
    elif emotion == 'happy' and sentiment == 'positive':
        total += 6
    elif emotion == 'neutral' and sentiment == 'neutral':
        total += 4

    if history_scores:
        recent = history_scores[-3:]
        avg_recent = sum(recent) / len(recent)
        if len(recent) >= 3 and avg_recent < 45 and total < 55:
            total -= 8
        last_score = history_scores[-1]
        total = total * 0.75 + last_score * 0.25

    total = max(0, min(100, total))
    score = int(round(total))
    accuracy = 'high' if score >= 60 or score <= 40 else 'medium'
    if score < 50 and sentiment == 'negative' and emotion in ['sad', 'angry', 'fear', 'disgust']:
        accuracy = 'high'

    return {
        'score': score,
        'accuracy': accuracy,
        'emotion': emotion,
        'sentiment': sentiment,
        'history_factor': bool(history_scores)
    }


def calculate_score(emotion, sentiment, history_scores=None):
    details = calculate_score_details(emotion, sentiment, history_scores=history_scores)
    return details['score']


def get_risk(score, history_scores=None):
    try:
        adjusted = score
        if history_scores:
            recent = history_scores[-3:]
            avg_recent = sum(recent) / len(recent)
            if len(recent) >= 3 and avg_recent < 40:
                adjusted -= 6
            elif len(recent) >= 3 and avg_recent > 65:
                adjusted += 3
        if adjusted < 35:
            return {
                'risk': 'High Stress Level',
                'message': 'Your recent trend is low. Try immediate relaxation and support.'
            }
        elif adjusted <= 60:
            return {
                'risk': 'Moderate Stress Level',
                'message': 'Your mood is mixed. Continue healthy habits and take mindful breaks.'
            }
        else:
            return {
                'risk': 'Low Stress Level',
                'message': 'Your wellness is on track. Keep practicing your self-care routine.'
            }
    except Exception as e:
        raise ValueError(f"Risk assessment failed: {str(e)}")


def get_score_label(score):
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    elif score >= 40:
        return 'Fair'
    else:
        return 'Needs Attention'
'''

recommendation = '''import random

BASE_RECOMMENDATIONS = {
    'low': [
        {'title': 'Nature Break', 'description': 'Step outside for a short walk and breathe fresh air to reduce tension.'},
        {'title': 'Guided Breathing', 'description': 'Try a 5-minute box breathing exercise to calm your nervous system.'},
        {'title': 'Gentle Stretching', 'description': 'Do some light stretching to release physical tension and improve mood.'}
    ],
    'medium': [
        {'title': 'Mindfulness Journal', 'description': 'Write down your thoughts for 10 minutes to process your emotions.'},
        {'title': 'Creative Expression', 'description': 'Sketch, journal, or listen to soothing music to shift your mindset.'},
        {'title': 'Connect with Someone', 'description': 'Reach out to a friend or family member for a positive conversation.'}
    ],
    'high': [
        {'title': 'Rest and Recovery', 'description': 'Take time to relax and prioritize sleep to restore emotional balance.'},
        {'title': 'Professional Support', 'description': 'Consider talking to a mental health professional for guidance.'},
        {'title': 'Calm Space', 'description': 'Create a quiet space and practice gentle breathing or meditation.'}
    ]
}

TIME_BASED = {
    'morning': 'A short energizing routine like stretching and mindful breathing can help set a calm tone for the day.',
    'afternoon': 'Take a pause, drink water, and do a quick grounding exercise to reset your energy.',
    'evening': 'A restful activity such as journaling or a guided body scan can help transition to a relaxed evening.'
}

EMOTION_TAGS = {
    'sad': 'Try a self-compassion exercise like noting three things that felt okay today.',
    'angry': 'Practice gentle breathing and allow some time to cool down before reacting.',
    'fear': 'Remind yourself of a small achievement and focus on one safe action.',
    'disgust': 'Choose a calming sensory activity such as soft music or a warm drink.',
    'happy': 'Keep the positive momentum by celebrating something small and steady.',
    'surprised': 'Reflect on what changed and take a few deep breaths to stay grounded.',
    'neutral': 'A simple mindful check-in can help clarify how you really feel.'
}


def _time_period(hour):
    if hour is None:
        return 'afternoon'
    if 5 <= hour < 12:
        return 'morning'
    if 12 <= hour < 18:
        return 'afternoon'
    return 'evening'


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
        recommendation_list = BASE_RECOMMENDATIONS['medium']
        label = 'Balanced'

        if score is None:
            score = 50

        if score < 35:
            recommendation_list = BASE_RECOMMENDATIONS['high']
            label = 'High Support'
        elif score <= 60:
            recommendation_list = BASE_RECOMMENDATIONS['medium']
            label = 'Moderate Support'
        else:
            recommendation_list = BASE_RECOMMENDATIONS['low']
            label = 'Low Support'

        suggestions = random.sample(recommendation_list, min(2, len(recommendation_list)))
        time_suggestion = TIME_BASED.get(period, TIME_BASED['afternoon'])
        emotion_suggestion = EMOTION_TAGS.get(str(emotion).lower(), '')

        summary = f"Based on your current mood score of {score}, we recommend {label.lower()} support. {time_suggestion}"
        if emotion_suggestion:
            summary += f" {emotion_suggestion}"

        structured = {
            'text': summary,
            'score': score,
            'label': label,
            'time': period,
            'emotion': emotion,
            'sentiment': sentiment,
            'suggestions': suggestions
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
'''

Path('backend/ai/sentiment.py').write_text(sentiment, encoding='utf-8')
Path('backend/ai/scoring.py').write_text(scoring, encoding='utf-8')
Path('backend/ai/recommendation.py').write_text(recommendation, encoding='utf-8')
