import os
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
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s\.,!\?]', '', text)
    text = re.sub(r'\s+', ' ', text)
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

            # Map LABEL_0, LABEL_1, LABEL_2 to sentiments
            if label == 'LABEL_2':
                sentiment = 'positive'
            elif label == 'LABEL_0':
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            # Adjust confidence based on text length
            if len(text) < 40 and sentiment == 'neutral':
                confidence = min(confidence + 0.07, 0.85)
            if len(text) < 25:
                confidence = max(0.55, confidence - 0.05)

            # Rule-based corrections for strong emotional words
            lower_text = text.lower()
            has_negative = any(word in lower_text for word in NEGATIVE_KEYWORDS)
            has_positive = any(word in lower_text for word in POSITIVE_KEYWORDS)

            if has_negative and sentiment == 'positive':
                sentiment = 'neutral'
                confidence = min(confidence, 0.65)
            if has_positive and sentiment == 'negative':
                sentiment = 'neutral'
                confidence = min(confidence, 0.7)

            # Boost confidence for strong emotional indicators
            if has_negative and sentiment == 'negative':
                confidence = min(confidence + 0.1, 0.95)
            if has_positive and sentiment == 'positive':
                confidence = min(confidence + 0.1, 0.95)

        except Exception as e:
            print(f"[AI] Sentiment pipeline failed: {e}")
            sentiment, confidence = _rule_based_sentiment(text)
    else:
        sentiment, confidence = _rule_based_sentiment(text)

    # Reject low confidence results
    if confidence < 0.5:
        sentiment = 'neutral'
        confidence = 0.5

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
