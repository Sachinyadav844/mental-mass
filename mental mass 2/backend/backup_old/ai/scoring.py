def calculate_score_details(emotion, sentiment, history_scores=None):
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
    elif emotion in ['happy', 'surprise'] and sentiment == 'negative':
        total -= 8  # Conflicting signals reduce score
    elif emotion in ['sad', 'angry', 'fear'] and sentiment == 'positive':
        total += 5  # Positive sentiment can help despite negative emotion

    # History smoothing with exponential moving average
    if history_scores:
        recent = history_scores[-5:]  # Use last 5 scores for better smoothing
        if len(recent) >= 3:
            # Calculate weighted average favoring recent scores
            weights = [0.1, 0.15, 0.2, 0.25, 0.3][:len(recent)]
            weights = [w / sum(weights) for w in weights]
            avg_recent = sum(s * w for s, w in zip(recent, weights))
            total = total * 0.7 + avg_recent * 0.3

    total = max(0, min(100, total))
    score = int(round(total))

    # Enhanced accuracy assessment
    accuracy = 'medium'
    if score >= 70 or score <= 30:
        accuracy = 'high'
    elif score >= 50 and emotion == 'uncertain':
        accuracy = 'low'
    elif sentiment == 'neutral' and emotion == 'neutral':
        accuracy = 'high'  # Neutral states are reliably detected

    return {
        'score': score,
        'accuracy': accuracy,
        'emotion': emotion,
        'sentiment': sentiment,
        'history_factor': bool(history_scores),
        'label': get_score_label(score)
    }

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
