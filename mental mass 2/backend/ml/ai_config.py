"""
Global AI model state - shared across all modules
"""

# Model availability flags
deepface_available = False
sentiment_available = False
chatbot_available = False

# Model instances
emotion_model = None
sentiment_model = None
gemini_model = None

# Error tracking
deepface_error = None
sentiment_error = None
chatbot_error = None