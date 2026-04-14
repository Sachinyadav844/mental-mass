"""
Sentiment: Rule-based analysis with optional HuggingFace Cardiff NLP RoBERTa.
When the model is missing or inference fails, uses rule-based fallback.
"""
import os
import re

from utils.error_handler import ValidationError
from config import (
    DEBUG,
    SENTIMENT_PRIMARY_MODEL,
    SENTIMENT_SHORT_TEXT_THRESHOLD,
    NEGATIVE_KEYWORDS,
    POSITIVE_KEYWORDS,
)

# Import global models from ai_config
from ml.ai_config import sentiment_available, sentiment_model

SENTIMENT_AVAILABLE = sentiment_available


def preprocess_for_inference(text: str) -> str:
    """Lowercase, collapse whitespace, strip; remove most special characters."""
    s = str(text).strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s\.,!\?\'\"-]", "", s)
    return s.strip()


def extract_emotion_keywords(text: str):
    """Deterministic keyword scan for API `keywords` field (no scoring)."""
    keywords = []
    text_lower = text.lower()
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            keywords.append(keyword)
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            keywords.append(keyword)
    return sorted(set(keywords))


def rule_based_sentiment(text: str) -> dict:
    """Rule-based sentiment analysis using keyword matching."""
    text_lower = text.lower()
    positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)

    total_keywords = positive_count + negative_count
    if total_keywords == 0:
        return {"sentiment": "neutral", "confidence": 0.5}

    if positive_count > negative_count:
        confidence = min(0.8, 0.5 + (positive_count / total_keywords) * 0.3)
        return {"sentiment": "positive", "confidence": confidence}
    elif negative_count > positive_count:
        confidence = min(0.8, 0.5 + (negative_count / total_keywords) * 0.3)
        return {"sentiment": "negative", "confidence": confidence}
    else:
        return {"sentiment": "neutral", "confidence": 0.6}


def _label_to_sentiment(label):
    label_upper = str(label).upper()
    if label_upper == "LABEL_2":
        return "positive"
    if label_upper == "LABEL_0":
        return "negative"
    if label_upper == "LABEL_1":
        return "neutral"
    return "neutral"


def analyze_sentiment(text):
    """
    Run Cardiff RoBERTa when loaded; otherwise rule-based fallback.
    Returns dict with sentiment, confidence; optional source for fallback paths.
    """
    if not isinstance(text, str):
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
        }

    text_input = preprocess_for_inference(text)[:512]
    if not text_input:
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
        }

    # Try ML model first
    if sentiment_model is not None:
        try:
            result = sentiment_model(text_input)[0]
            if DEBUG or os.getenv("SENTIMENT_DEBUG", "").lower() in ("1", "true", "yes"):
                print("Input text:", text_input)
                print("Model output:", result)

            label = result.get("label", "LABEL_1")
            confidence = float(result.get("score", 0.5))
            sentiment = _label_to_sentiment(label)

            print(f"[SENTIMENT] ML Result: sentiment={sentiment}, confidence={confidence}")
            return {
                "sentiment": sentiment,
                "confidence": round(confidence, 4),
            }
        except Exception as e:
            print("Sentiment ML error:", e)
            print("[SENTIMENT] Falling back to rule-based analysis")

    # Rule-based fallback
    result = rule_based_sentiment(text_input)
    print(f"[SENTIMENT] Rule-based Result: sentiment={result['sentiment']}, confidence={result['confidence']}")
    return {
        "sentiment": result["sentiment"],
        "confidence": round(result["confidence"], 4),
    }


def is_sentiment_available():
    return SENTIMENT_AVAILABLE


def analyze_text_sentiment(text):
    """
    Public API for /analyze_text: same response keys as before.
    """
    if not text or not isinstance(text, str):
        raise ValidationError("Text must be a non-empty string")

    stripped = str(text).strip()
    if not stripped:
        raise ValidationError("Text field is required and cannot be empty")

    pre = preprocess_for_inference(stripped)
    word_count = len(pre.split()) if pre else 0
    is_short_text = word_count < SENTIMENT_SHORT_TEXT_THRESHOLD

    result = analyze_sentiment(stripped)
    model_used = SENTIMENT_PRIMARY_MODEL if SENTIMENT_AVAILABLE else "unavailable"

    return {
        "sentiment": result["sentiment"],
        "confidence": float(result["confidence"]),
        "keywords": extract_emotion_keywords(pre) if pre else [],
        "model_used": model_used,
        "word_count": word_count,
        "is_short_text": is_short_text,
    }


def get_sentiment_numeric_score(sentiment):
    from config import SENTIMENT_NUMERIC_MAP

    return SENTIMENT_NUMERIC_MAP.get(sentiment, 5)
