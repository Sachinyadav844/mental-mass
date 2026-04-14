"""
MentalMass Backend - Flask Application
AI-based mental wellness monitoring system
"""
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configuration & DB (no route imports yet)
from config import (
    DEBUG,
    ENV,
    FLASK_HOST,
    FLASK_PORT,
    CORS_METHODS,
    CORS_ALLOW_HEADERS,
    JWT_SECRET_KEY,
    JWT_ACCESS_TOKEN_EXPIRES,
)
from database import init_db
from utils.error_handler import register_error_handlers
from utils.socketio_manager import init_socketio

# Load DeepFace + HuggingFace before blueprints import ml-heavy modules
print("Loading AI models...")

from ml.ai_config import deepface_available, sentiment_available, chatbot_available, emotion_model, sentiment_model, gemini_model, deepface_error, sentiment_error, chatbot_error

# DeepFace Fix - Skip for now to avoid TensorFlow issues
try:
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Reduce TensorFlow logging
    # Temporarily disable DeepFace to avoid startup issues
    deepface_available = False
    emotion_model = None
    deepface_error = "DeepFace temporarily disabled due to TensorFlow compatibility issues"
    print("DeepFace: Temporarily disabled - will use fallback")
except Exception as e:
    deepface_available = False
    emotion_model = None
    deepface_error = str(e)
    print("DeepFace error:", e)

# HuggingFace Fix - Skip for now
try:
    # Temporarily disable transformers to avoid import issues
    sentiment_available = False
    sentiment_model = None
    sentiment_error = "Transformers temporarily disabled due to compatibility issues"
    print("Sentiment: Temporarily disabled - will use rule-based analysis")
except Exception as e:
    sentiment_available = False
    sentiment_model = None
    sentiment_error = str(e)
    print("Sentiment error:", e)

# Gemini Fix
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        chatbot_available = True
        print("Gemini chatbot OK")
    else:
        raise ValueError("GEMINI_API_KEY not found in environment")
except Exception as e:
    chatbot_available = False
    gemini_model = None
    chatbot_error = str(e)
    print("Gemini error:", e)

# Update ai_config with loaded models
import ml.ai_config as ai_config
ai_config.chatbot_available = chatbot_available
ai_config.gemini_model = gemini_model
ai_config.chatbot_error = chatbot_error

# Gemini Fix
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        chatbot_available = True
        print("Gemini chatbot loaded successfully")
    else:
        raise ValueError("GEMINI_API_KEY not found in environment")
except Exception as e:
    print("Gemini error:", e)
    chatbot_available = False
    gemini_model = None
    chatbot_error = str(e)

# Update ai_config with loaded models
import ml.ai_config as ai_config
ai_config.chatbot_available = chatbot_available
ai_config.gemini_model = gemini_model
ai_config.chatbot_error = chatbot_error

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

app = Flask(__name__)

app.config["DEBUG"] = DEBUG
app.config["ENV"] = ENV
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES
app.config["JSON_SORT_KEYS"] = False

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=CORS_ALLOW_HEADERS,
    methods=CORS_METHODS,
    max_age=3600,
)

jwt = JWTManager(app)

# Initialize Socket.IO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*")
init_socketio(socketio)

from routes.auth_routes import auth_bp
from routes.face_routes import face_bp
from routes.text_routes import text_bp
from routes.score_routes import score_bp
from routes.recommendation_routes import recommendation_bp
from routes.session_routes import session_bp
from routes.assessment_routes import assessment_bp
from routes.chatbot_routes import chatbot_bp

from utils.error_handler import success_response
print(f"[APP] Environment: {ENV}")
print(f"[APP] Debug: {DEBUG}")

try:
    init_db()
    print("[APP] Database initialized successfully")
except Exception as e:
    print(f"[APP] Database initialization error: {str(e)}")
    sys.exit(1)

register_error_handlers(app)

app.register_blueprint(auth_bp)
app.register_blueprint(face_bp)
app.register_blueprint(text_bp)
app.register_blueprint(score_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(session_bp)
app.register_blueprint(assessment_bp)
app.register_blueprint(chatbot_bp)

print("[APP] Blueprints registered successfully")


@app.route("/", methods=["GET"])
def health_check():
    """Root health check with model flags (API-compatible extras preserved)."""
    return success_response(
        {
            "message": "MENTALMASS Backend is running",
            "version": "2.0",
            "status": "healthy",
            "emotion_detection": deepface_available,
            "sentiment": sentiment_available,
            "chatbot": chatbot_available,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


if __name__ == "__main__":
    print(f"[APP] Starting MentalMass Backend on {FLASK_HOST}:{FLASK_PORT}")
    print("[APP] Socket.IO enabled for real-time updates")
    socketio.run(
        app,
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True,
        use_reloader=False,
    )
