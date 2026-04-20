"""
MentalMass Backend Configuration
"""
import os
from pathlib import Path

# ============================================================================
# APPLICATION
# ============================================================================
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENV = os.getenv('FLASK_ENV', 'production')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# ============================================================================
# CORS
# ============================================================================
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',     # Vite default
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'http://localhost:3001',
]

CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']

# ============================================================================
# JWT
# ============================================================================
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mentalmass_secret_key_2024_production')
JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds

# ============================================================================
# DATABASE
# ============================================================================
BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / 'data'
DB_PATH = DB_DIR / 'mentalmass.db'
DB_URI = f'sqlite:///{DB_PATH}'

# Ensure data directory exists
DB_DIR.mkdir(exist_ok=True)

# ============================================================================
# FILE UPLOADS
# ============================================================================
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}

# ============================================================================
# ML MODELS
# ============================================================================
# DeepFace
DEEPFACE_DETECTOR = 'opencv'
DEEPFACE_ENFORCE_DETECTION = False
DEEPFACE_NUM_PASSES = 3  # Number of multi-pass runs for emotion ensemble
DEEPFACE_CONFIDENCE_THRESHOLD = 0.40  # 40% confidence threshold

# Sentiment Analysis
SENTIMENT_PRIMARY_MODEL = 'cardiffnlp/twitter-roberta-base-sentiment'
SENTIMENT_FALLBACK_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'
SENTIMENT_SHORT_TEXT_THRESHOLD = 5  # words

# Chatbot
CHATBOT_MODEL = 'microsoft/DialoGPT-medium'
CHATBOT_MAX_HISTORY = 5
CHATBOT_SYSTEM_PROMPT = """You are a mental wellness assistant. 
Only answer questions about mental health, emotions, stress, anxiety, and wellness. 
Refuse all other topics politely and redirect to mental wellness topics."""

CHATBOT_OFF_TOPIC_KEYWORDS = [
    'python', 'javascript', 'code', 'programming', 'algorithm',
    'politics', 'trump', 'biden', 'election', 'vote',
    'sports', 'football', 'baseball', 'soccer', 'game',
    'weather', 'news', 'movie', 'game', 'cryptocurrency',
]

# Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# Image Processing
IMAGE_RESIZE_WIDTH = 224
IMAGE_RESIZE_HEIGHT = 224
IMAGE_BLUR_KERNEL = (3, 3)

# ============================================================================
# EMOTION MAPPINGS
# ============================================================================
EMOTION_NUMERIC_MAP = {
    'happy': 90,
    'surprised': 60,
    'neutral': 60,
    'fear': 30,
    'sad': 30,
    'angry': 20,
    'disgust': 15,
    'uncertain': 50,
}

# ============================================================================
# SENTIMENT MAPPINGS
# ============================================================================
SENTIMENT_NUMERIC_MAP = {
    'positive': 90,
    'neutral': 60,
    'negative': 30,
}

# ============================================================================
# MOOD SCORE WEIGHTING
# ============================================================================
MOOD_SCORE_WEIGHTS = {
    'facial_emotion': 0.60,  # Updated for higher accuracy
    'text_sentiment': 0.40,   # Updated for higher accuracy
    'user_self_score': 0.00,  # Removed for accuracy
}

# ============================================================================
# RISK LEVELS
# ============================================================================
RISK_THRESHOLDS = {
    'Low Risk': (60, 100),      # score >= 60
    'Moderate Risk': (35, 59),  # 35 <= score < 60
    'High Risk': (0, 34),       # score < 35
}

RISK_COLORS = {
    'Low Risk': '#22c55e',      # green
    'Moderate Risk': '#eab308',  # yellow
    'High Risk': '#ef4444',      # red
}

# ============================================================================
# SENTIMENT KEYWORDS
# ============================================================================
NEGATIVE_KEYWORDS = [
    'sad', 'depressed', 'anxious', 'stress', 'tired', 'overwhelmed',
    'upset', 'angry', 'worried', 'afraid', 'lonely', 'hopeless',
    'desperate', 'suicidal', 'pain', 'suffer', 'hurt', 'cry'
]

POSITIVE_KEYWORDS = [
    'happy', 'good', 'better', 'relaxed', 'calm', 'grateful',
    'safe', 'hopeful', 'supported', 'okay', 'fine', 'great',
    'wonderful', 'joy', 'love', 'peace', 'content', 'proud'
]

# ============================================================================
# LOGGING
# ============================================================================
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
ERROR_LOG_FILE = LOG_DIR / 'errors.log'
ACCESS_LOG_FILE = LOG_DIR / 'access.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# RECOMMENDATIONS DATA
# ============================================================================
RECOMMENDATIONS_FILE = BASE_DIR / 'data' / 'recommendations.json'

# ============================================================================
# SESSION & USER DATA
# ============================================================================
SESSIONS_LIMIT = 30  # Return last 30 sessions
ASSESSMENT_QUESTIONS = [
    {
        'id': 1,
        'text': 'I have been feeling tense or wound up',
        'category': 'anxiety'
    },
    {
        'id': 2,
        'text': 'I have been worrying a lot',
        'category': 'anxiety'
    },
    {
        'id': 3,
        'text': 'I have been feeling sad or miserable',
        'category': 'depression'
    },
    {
        'id': 4,
        'text': 'I have not been able to enjoy normal daily activities',
        'category': 'depression'
    },
    {
        'id': 5,
        'text': 'I have felt tired or low on energy',
        'category': 'fatigue'
    }
]
