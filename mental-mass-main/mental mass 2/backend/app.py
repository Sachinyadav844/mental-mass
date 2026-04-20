"""
MentalMass Backend - Flask Application
AI-based mental wellness monitoring system
"""
import os
import sys

# TensorFlow / Keras: MUST be set before any TF, keras, deepface, or transformers import
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

from datetime import datetime

from dotenv import load_dotenv

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

# Initialize DeepFace + HuggingFace before blueprints (routes import ml modules)
print("[APP] Loading AI models...")
from ml.ai_bootstrap import init_ai_models

init_ai_models()

import ml.ai_config as ai_config

# Gemini (required chatbot integration)
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("API key missing")

genai.configure(api_key=GEMINI_API_KEY)
ai_config.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
ai_config.chatbot_available = True
ai_config.chatbot_error = None
print("[APP] Gemini chatbot OK")

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
    import ml.ai_config as ac

    return success_response(
        {
            "message": "MENTALMASS Backend is running",
            "version": "2.0",
            "status": "healthy",
            "emotion_detection": ac.deepface_available,
            "sentiment": ac.sentiment_available,
            "chatbot": ac.chatbot_available,
            "deepface_error": ac.deepface_error,
            "sentiment_error": ac.sentiment_error,
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
