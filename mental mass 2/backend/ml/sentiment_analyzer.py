"""
Sentiment: HuggingFace Cardiff NLP RoBERTa only. No rule-based fallback.
When the model is missing or inference fails, returns neutral with fixed confidence.
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

sentiment_model = None
SENTIMENT_AVAILABLE = False


def _pipeline_device():
    """Use GPU when available; otherwise CPU (-1)."""
    try:
        import torch

        if torch.cuda.is_available():
            return 0
    except ImportError:
        pass
    return -1


def initialize_sentiment_pipeline():
    global sentiment_model, SENTIMENT_AVAILABLE

    try:
        from transformers import pipeline

        print("[SENTIMENT] Loading HuggingFace model...")
        device = _pipeline_device()
        sentiment_model = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_PRIMARY_MODEL,
            device=device,
        )
        SENTIMENT_AVAILABLE = True
        print("Sentiment model loaded successfully")
    except Exception as e:
        print("Sentiment model failed:", e)
        sentiment_model = None
        SENTIMENT_AVAILABLE = False


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
    Run Cardiff RoBERTa when loaded; otherwise neutral fallback.
    Returns dict with sentiment, confidence; optional source for fallback paths.
    """
    if not isinstance(text, str):
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "source": "fallback",
        }

    text_input = preprocess_for_inference(text)[:512]
    if not text_input:
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "source": "fallback",
        }

    if sentiment_model is None:
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "source": "fallback",
        }

    try:
        result = sentiment_model(text_input)[0]
        if DEBUG or os.getenv("SENTIMENT_DEBUG", "").lower() in ("1", "true", "yes"):
            print("Input text:", text_input)
            print("Model output:", result)

        label = result.get("label", "LABEL_1")
        confidence = float(result.get("score", 0.5))
        sentiment = _label_to_sentiment(label)

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
        }
    except Exception as e:
        print("Sentiment error:", e)
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "source": "fallback",
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
    source = result.get("source")
    model_used = (
        SENTIMENT_PRIMARY_MODEL
        if SENTIMENT_AVAILABLE and source != "fallback"
        else "fallback"
    )

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
