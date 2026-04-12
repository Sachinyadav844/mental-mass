"""
Sentiment: HuggingFace Cardiff NLP RoBERTa at startup; keyword/rule fallback if the model is missing.
"""
import re

from utils.error_handler import MLModelError, ValidationError
from config import (
    SENTIMENT_PRIMARY_MODEL,
    SENTIMENT_FALLBACK_MODEL,
    SENTIMENT_SHORT_TEXT_THRESHOLD,
    NEGATIVE_KEYWORDS,
    POSITIVE_KEYWORDS,
)

sentiment_model = None
_sentiment_model_name = None
SENTIMENT_AVAILABLE = False


def initialize_sentiment_pipeline():
    """Load transformers sentiment pipeline once at startup."""
    global sentiment_model, _sentiment_model_name, SENTIMENT_AVAILABLE
    try:
        from transformers import pipeline as hf_pipeline

        try:
            print("[SENTIMENT] Loading model:", SENTIMENT_PRIMARY_MODEL)
            sentiment_model = hf_pipeline(
                "sentiment-analysis",
                model=SENTIMENT_PRIMARY_MODEL,
            )
            _sentiment_model_name = SENTIMENT_PRIMARY_MODEL
            SENTIMENT_AVAILABLE = True
            print("Sentiment model loaded")
            return
        except Exception as e:
            print("Sentiment failed:", e)
            print("[SENTIMENT] Trying fallback:", SENTIMENT_FALLBACK_MODEL)
            sentiment_model = hf_pipeline(
                "sentiment-analysis",
                model=SENTIMENT_FALLBACK_MODEL,
            )
            _sentiment_model_name = SENTIMENT_FALLBACK_MODEL
            SENTIMENT_AVAILABLE = True
            print("Sentiment model loaded (fallback)")
    except Exception as e:
        sentiment_model = None
        _sentiment_model_name = None
        SENTIMENT_AVAILABLE = False
        print("Sentiment failed:", e)


def load_sentiment_model(model_name=None):
    """Return active pipeline, loading if needed (e.g. after fork)."""
    global sentiment_model, _sentiment_model_name, SENTIMENT_AVAILABLE

    model_name = model_name or SENTIMENT_PRIMARY_MODEL
    if sentiment_model is not None and (model_name is None or _sentiment_model_name == model_name):
        return sentiment_model

    try:
        from transformers import pipeline as hf_pipeline

        sentiment_model = hf_pipeline("sentiment-analysis", model=model_name)
        _sentiment_model_name = model_name
        SENTIMENT_AVAILABLE = True
        return sentiment_model
    except Exception as e:
        print(f"[SENTIMENT] Failed to load {model_name}: {str(e)}")
        raise MLModelError(f"Failed to load sentiment model: {str(e)}")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"[^\w\s\.,!\?\'\"-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_emotion_keywords(text):
    keywords = []
    text_lower = text.lower()
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            keywords.append(keyword)
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            keywords.append(keyword)
    return list(set(keywords))


def apply_keyword_boosting(sentiment, confidence, text):
    text_lower = text.lower()
    word_count = len(text.split())
    if word_count >= SENTIMENT_SHORT_TEXT_THRESHOLD:
        return sentiment, confidence
    has_negative = any(keyword in text_lower for keyword in NEGATIVE_KEYWORDS)
    has_positive = any(keyword in text_lower for keyword in POSITIVE_KEYWORDS)
    if has_negative and not has_positive:
        return "negative", min(confidence + 0.15, 0.98)
    if has_positive and not has_negative:
        return "positive", min(confidence + 0.15, 0.98)
    if has_negative and has_positive:
        return "neutral", max(confidence - 0.10, 0.3)
    return sentiment, confidence


def _label_to_sentiment(label):
    label_upper = str(label).upper()
    if label_upper == "LABEL_2" or label_upper == "POSITIVE":
        return "positive"
    if label_upper == "LABEL_0" or label_upper == "NEGATIVE":
        return "negative"
    if label_upper == "LABEL_1" or label_upper == "NEUTRAL":
        return "neutral"
    return "neutral"


def analyze_sentiment(text):
    if not text or not isinstance(text, str):
        raise ValidationError("Text must be a non-empty string")

    text = clean_text(text)
    if not text:
        raise ValidationError("Text is empty after cleaning")

    word_count = len(text.split())
    is_short_text = word_count < SENTIMENT_SHORT_TEXT_THRESHOLD

    clf = sentiment_model
    if clf is None:
        return _rule_based_sentiment_analysis(text)

    try:
        text_input = text[:512]
        out = clf(text_input)[0]
        label = out.get("label", "LABEL_1")
        confidence = float(out.get("score", 0.5))
        sentiment = _label_to_sentiment(label)
        keywords = extract_emotion_keywords(text)
        if is_short_text:
            sentiment, confidence = apply_keyword_boosting(sentiment, confidence, text)
        if confidence < 0.3:
            sentiment = "neutral"
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "keywords": keywords,
            "model_used": "cardiffnlp/twitter-roberta-base-sentiment"
            if _sentiment_model_name == SENTIMENT_PRIMARY_MODEL
            else (_sentiment_model_name or "transformers"),
            "word_count": word_count,
            "is_short_text": is_short_text,
        }
    except Exception as e:
        print(f"[SENTIMENT] Transformer inference failed: {e} — using rule-based fallback")
        return _rule_based_sentiment_analysis(text)


def is_sentiment_available():
    return SENTIMENT_AVAILABLE


def analyze_text_sentiment(text):
    result = analyze_sentiment(text)
    return {
        "sentiment": result["sentiment"],
        "confidence": result["confidence"],
        "keywords": result.get("keywords", []),
        "model_used": result.get("model_used", "unknown"),
        "word_count": result.get("word_count", len(str(text).split())),
        "is_short_text": result.get("is_short_text", False),
    }


def get_sentiment_numeric_score(sentiment):
    from config import SENTIMENT_NUMERIC_MAP

    return SENTIMENT_NUMERIC_MAP.get(sentiment, 5)


def _rule_based_sentiment_analysis(text):
    text_lower = text.lower()
    negative_count = sum(text_lower.count(word) for word in NEGATIVE_KEYWORDS)
    positive_count = sum(text_lower.count(word) for word in POSITIVE_KEYWORDS)
    if negative_count > positive_count:
        sentiment = "negative"
        confidence = min(0.5 + (negative_count * 0.1), 0.95)
    elif positive_count > negative_count:
        sentiment = "positive"
        confidence = min(0.5 + (positive_count * 0.1), 0.95)
    else:
        sentiment = "neutral"
        confidence = 0.5
    keywords = extract_emotion_keywords(text)
    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "keywords": keywords,
        "model_used": "rule_based",
        "word_count": len(text.split()),
        "is_short_text": len(text.split()) < SENTIMENT_SHORT_TEXT_THRESHOLD,
    }
