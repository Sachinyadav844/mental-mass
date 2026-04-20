"""
Initialize DeepFace and HuggingFace models once at process startup.
Must run before importing route blueprints that depend on ml.*.
"""


def init_ai_models():
    print("Loading AI models...")
    from ml.emotion_detector import initialize_deepface
    from ml.sentiment_analyzer import initialize_sentiment_pipeline

    initialize_deepface()
    initialize_sentiment_pipeline()
    print("[AI] Startup model initialization finished.")
