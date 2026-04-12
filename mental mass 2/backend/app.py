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

# Load DeepFace + HuggingFace before blueprints import ml-heavy modules
from ml.ai_bootstrap import init_ai_models

init_ai_models()

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.auth_routes import auth_bp
from routes.face_routes import face_bp
from routes.text_routes import text_bp
from routes.score_routes import score_bp
from routes.recommendation_routes import recommendation_bp
from routes.session_routes import session_bp
from routes.assessment_routes import assessment_bp
from routes.chatbot_routes import chatbot_bp

from utils.error_handler import success_response

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

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

print("[APP] Initializing MentalMass Backend")
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
    from ml.emotion_detector import DEEPFACE_AVAILABLE
    from ml.sentiment_analyzer import is_sentiment_available

    deepface_available = DEEPFACE_AVAILABLE
    return success_response(
        {
            "message": "MENTALMASS Backend is running",
            "version": "2.0",
            "status": "healthy",
            "emotion_detection": {
                "available": deepface_available,
                "deepface_available": deepface_available,
            },
            "sentiment_available": is_sentiment_available(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


if __name__ == "__main__":
    from ml.sentiment_analyzer import sentiment_model as _sm, initialize_sentiment_pipeline

    if _sm is None:
        initialize_sentiment_pipeline()

    print(f"[APP] Starting MentalMass Backend on {FLASK_HOST}:{FLASK_PORT}")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=DEBUG,
        use_reloader=False,
        threaded=True,
    )
