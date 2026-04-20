# MentalMass Backend - Complete Implementation Guide

## ✅ Implementation Status

All backend components have been completely refactored and updated with production-ready code:

### Core Files Created/Updated
- ✅ **app.py** - Main Flask application with blueprint registration
- ✅ **config.py** - Centralized configuration (ML models, weights, thresholds)
- ✅ **database.py** - SQLite database models and management
- ✅ **requirements.txt** - Updated dependencies

### ML Module (ml/)
- ✅ **emotion_detector.py** - Multi-pass DeepFace emotion analysis (fixes PROBLEM 2 & 3)
- ✅ **sentiment_analyzer.py** - HuggingFace sentiment with keyword boosting (fixes PROBLEM 4)
- ✅ **score_calculator.py** - Weighted mood score (fixes PROBLEM 5)
- ✅ **face_validator.py** - Haar cascade face detection

### Route Modules (routes/)
- ✅ **face_routes.py** - /analyze_face endpoint (fixes PROBLEM 1)
- ✅ **text_routes.py** - /analyze_text endpoint
- ✅ **score_routes.py** - /calculate_score endpoint
- ✅ **recommendation_routes.py** - /recommendation endpoint
- ✅ **session_routes.py** - /sessions endpoints (fixes PROBLEM 8)
- ✅ **assessment_routes.py** - /assessment endpoints
- ✅ **chatbot_routes.py** - /chatbot endpoint (fixes PROBLEM 6)
- ✅ **auth_routes.py** - /register, /login, /profile endpoints

### Utility Modules (utils/)
- ✅ **error_handler.py** - Global error handling (fixes PROBLEM 7)
- ✅ **logger.py** - Logging setup
- ✅ **image_utils.py** - Image processing utilities

---

## 🔧 PROBLEM FIXES SUMMARY

### PROBLEM 1 ✅ - 422 ERROR (CRITICAL)
**Fixed in:** `routes/face_routes.py` → `/analyze_face` endpoint

```python
# Handles BOTH:
# a) multipart/form-data → file upload (request.files["image"])
# b) JSON base64 → webcam (request.json["image_data"])

if request.files and 'image' in request.files:
    img = load_image_from_file(request.files['image'])
elif request.is_json and 'image_data' in request.json:
    img = load_image_from_base64(request.json['image_data'])
else:
    return error_response(ImageProcessingError(...))
```

### PROBLEM 2 ✅ - LOW EMOTION ACCURACY
**Fixed in:** `ml/emotion_detector.py` → `analyze_emotion()` function

- ✅ Multi-pass ensemble (3 runs with DeepFace)
- ✅ Averages emotion probabilities across passes
- ✅ Applies confidence threshold (40% minimum)
- ✅ Preprocessing pipeline:
  - cv2.resize to 224x224
  - cv2.cvtColor to RGB
  - cv2.equalizeHist for brightness
  - cv2.GaussianBlur for noise

### PROBLEM 3 ✅ - NO FACE DETECTION VALIDATION
**Fixed in:** `ml/face_validator.py`

Uses OpenCV Haar cascade with proper error handling:
```python
def validate_face_detected(img):
    faces = detect_faces(img)  # Haar cascade
    if len(faces) == 0:
        raise NoFaceDetectedError('No faces detected in the image')
    return {
        'detected': True,
        'face_box': {...},
        'all_faces': [...]
    }
```

### PROBLEM 4 ✅ - INACCURATE SENTIMENT ANALYSIS
**Fixed in:** `ml/sentiment_analyzer.py`

- ✅ Primary model: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- ✅ Fallback model: `distilbert-base-uncased-finetuned-sst-2-english`
- ✅ Keyword boosting for short text (<5 words)
- ✅ Returns: sentiment label, confidence score, emotion keywords

### PROBLEM 5 ✅ - RANDOM MOOD SCORE
**Fixed in:** `ml/score_calculator.py` → `calculate_mood_score()`

Weighted logic with proper mappings:
```python
MOOD_SCORE_WEIGHTS = {
    'facial_emotion': 0.40,
    'text_sentiment': 0.35,
    'user_self_score': 0.25,
}

EMOTION_NUMERIC_MAP = {
    'happy': 9, 'surprised': 6, 'neutral': 6,
    'fear': 3, 'sad': 2, 'angry': 2, 'disgust': 1,
}

SENTIMENT_NUMERIC_MAP = {
    'positive': 9, 'neutral': 5, 'negative': 2,
}

RISK_THRESHOLDS = {
    'low': (7, 10),       # >= 7 → green
    'moderate': (4, 6.99),  # 4-7 → yellow
    'high': (0, 3.99),    # < 4 → red
}
```

### PROBLEM 6 ✅ - UNSTABLE CHATBOT
**Fixed in:** `routes/chatbot_routes.py`

- ✅ Uses `microsoft/DialoGPT-medium`
- ✅ System prompt with mental wellness focus
- ✅ Maintains conversation history (last 5 turns)
- ✅ Topic guard with off-topic keyword detection
- ✅ Graceful fallback responses

### PROBLEM 7 ✅ - WEAK ERROR HANDLING
**Fixed in:** `utils/error_handler.py`

Global error handling with:
- ✅ Try/except with specific exception types
- ✅ Custom error response format
- ✅ Logging to errors.log
- ✅ JSON error responses (never crashes)

### PROBLEM 8 ✅ - SESSION DATA STORAGE
**Fixed in:** `database.py` and `routes/session_routes.py`

SQLite database with tables:
- ✅ `users` - User accounts with bcrypt hashing
- ✅ `sessions` - Analysis sessions with full data
- ✅ `assessments` - Self-assessment responses
- ✅ GET /sessions → last 30 sessions
- ✅ GET /sessions/stats → aggregate statistics

---

## 🚀 INSTALLATION & SETUP

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**
- Flask 3.0.0
- flask-cors 4.0.0
- flask-jwt-extended 4.5.3
- opencv-python 4.9.0.80
- deepface 0.0.93
- transformers 4.40.0
- torch 2.2.0
- bcrypt 4.1.2
- SQLAlchemy 2.0.30

### 2. Environment Setup
Create `.env` file in backend/:
```
FLASK_ENV=development
DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
JWT_SECRET_KEY=your_secret_key_2024
```

### 3. Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

This creates:
- `data/mentalmass.db` - SQLite database with WAL mode
- `logs/` - Error and access logs

### 4. Run Backend
```bash
python app.py
```

Server starts at `http://0.0.0.0:5000`

---

## 📡 API ENDPOINTS REFERENCE

### Authentication (Public)
```
POST /register
  Input:  {name, email, password}
  Output: {user, token}

POST /login
  Input:  {email, password}
  Output: {user, token}

GET /profile
  Auth: Required
  Output: {user}
```

### Face Analysis (Public)
```
POST /analyze_face
  Input:  multipart/form-data (image) OR JSON (image_data)
  Output: {emotion, confidence, all_emotions, face_detected, face_box, passes}
```

### Text Analysis (Protected)
```
POST /analyze_text
  Input:  {text}
  Output: {sentiment, confidence, keywords, model_used, word_count}
```

### Mood Scoring (Protected)
```
POST /calculate_score
  Input:  {emotion, sentiment, self_score}
  Output: {score, risk_level, risk_color, breakdown}
```

### Recommendations (Protected)
```
POST /recommendation
  Input:  {score, risk_level, emotion}
  Output: {category, suggestions, emergency_resources}
```

### Sessions (Protected)
```
GET /sessions?limit=30
  Output: {sessions, total}

POST /sessions
  Input:  {emotion, sentiment, mood_score, risk_level, ...}
  Output: {session_id, timestamp}

GET /sessions/stats
  Output: {total_sessions, avg_mood_score, emotion_distribution}

GET /sessions/{session_id}
  Output: {session}
```

### Assessment (Protected)
```
GET /assessment/questions
  Output: {questions, total_questions}

POST /assessment
  Input:  {answers: [0-3, 0-3, ...]}
  Output: {total_score, risk_level, recommendations}
```

### Chatbot (Protected)
```
POST /chatbot
  Input:  {message, session_id}
  Output: {reply, session_id, turn_count, model}
```

### Health
```
GET /
  Output: {status, version, deepface_available}

GET /health
  Output: {status, ml_models}
```

---

## 🧠 ML MODEL CONFIGURATION

All settings in `config.py`:

### DeepFace
```python
DEEPFACE_NUM_PASSES = 3  # Multi-pass for accuracy
DEEPFACE_CONFIDENCE_THRESHOLD = 0.40  # 40% minimum
DEEPFACE_ENFORCE_DETECTION = False  # Use Haar cascade
```

### Sentiment
```python
SENTIMENT_PRIMARY_MODEL = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
SENTIMENT_FALLBACK_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'
SENTIMENT_SHORT_TEXT_THRESHOLD = 5  # Apply boosting for < 5 words
```

### Chatbot
```python
CHATBOT_MODEL = 'microsoft/DialoGPT-medium'
CHATBOT_MAX_HISTORY = 5
CHATBOT_SYSTEM_PROMPT = '...'
```

---

## 📊 DATABASE SCHEMA

### users table
```sql
id (primary key)
name
email (unique)
password_hash (bcrypt)
created_at
updated_at
firebase_auth (boolean)
```

### sessions table
```sql
id (primary key)
user_id
timestamp
emotion, emotion_confidence, all_emotions
sentiment, sentiment_confidence, sentiment_keywords
mood_score, risk_level, risk_color
face_detected, face_box
self_score
image_source
```

### assessments table
```sql
id (primary key)
user_id
timestamp
answers (JSON array)
total_score
risk_level
```

---

## 🔐 SECURITY FEATURES

1. **Password Hashing**: bcrypt with salt
2. **JWT Authentication**: 24-hour tokens
3. **CORS**: Limited to React frontend
4. **Error Logging**: All errors logged to `logs/errors.log`
5. **SQLite WAL Mode**: Concurrent read safety

---

## 📝 TESTING THE BACKEND

### 1. Test Face Analysis
```bash
# File upload
curl -X POST http://localhost:5000/analyze_face \
  -F "image=@test_image.jpg"

# Webcam (base64 JSON)
curl -X POST http://localhost:5000/analyze_face \
  -H "Content-Type: application/json" \
  -d '{"image_data":"data:image/jpeg;base64,/9j/4AAQSkZJRg..."}'
```

### 2. Test Text Analysis (with JWT)
```bash
# Get token first
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"password123"}'

# Extract token from response, then:
curl -X POST http://localhost:5000/analyze_text \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text":"I feel terrible today"}'
```

### 3. Full Pipeline Test
1. Register user
2. Upload face image → get emotion
3. Analyze text → get sentiment
4. Calculate mood score → get risk level
5. Get recommendations
6. Save to sessions

---

## 🐛 TROUBLESHOOTING

### DeepFace Not Available
- Ensure TensorFlow is installed: `pip install tf-keras tensorflow`
- May take time to download models on first run

### Sentiment Model Slow
- Models are lazy-loaded on first use
- Consider pre-warming by calling `/analyze_text` once on startup

### Database Lock
- SQLite WAL mode prevents most lock issues
- Multiple readers, single writer

### JWT Token Expired
- Default: 24 hours (`JWT_ACCESS_TOKEN_EXPIRES = 86400`)
- User must re-login to get new token

---

## 📦 FILE STRUCTURE

```
backend/
├── app.py                           ← Main Flask app
├── config.py                        ← Configuration
├── database.py                      ← SQLite ORM
├── requirements.txt                 ← Dependencies
├── data/
│   ├── mentalmass.db               ← SQLite database
│   └── recommendations.json        ← Suggestion bank
├── logs/
│   ├── errors.log                  ← Error log
│   └── access.log                  ← Access log
├── ml/
│   ├── __init__.py
│   ├── emotion_detector.py         ← DeepFace multi-pass
│   ├── sentiment_analyzer.py       ← HuggingFace
│   ├── face_validator.py           ← Haar cascade
│   └── score_calculator.py         ← Weighted scoring
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py              ← Authentication
│   ├── face_routes.py              ← Face analysis
│   ├── text_routes.py              ← Text analysis
│   ├── score_routes.py             ← Mood scoring
│   ├── recommendation_routes.py    ← Recommendations
│   ├── session_routes.py           ← Sessions
│   ├── assessment_routes.py        ← Assessments
│   └── chatbot_routes.py           ← Chatbot
└── utils/
    ├── __init__.py
    ├── error_handler.py            ← Error handling
    ├── logger.py                   ← Logging
    └── image_utils.py              ← Image processing
```

---

## ✨ KEY IMPROVEMENTS

1. **Production-Ready Architecture**: Modular, scalable, maintainable
2. **Comprehensive Error Handling**: Never crashes, always returns JSON
3. **Database**: SQLite with proper ORM and concurrent access
4. **ML Accuracy**: Multi-pass ensemble emotion detection
5. **Security**: Password hashing, JWT auth, input validation
6. **Performance**: Lazy loading of models, connection pooling
7. **Logging**: Structured error and access logs
8. **Documentation**: Inline code comments and this guide

---

## 🎯 NEXT STEPS

1. **Test thoroughly** with React frontend
2. **Monitor logs** in `logs/errors.log` for issues
3. **Adjust weights** in `config.py` based on real data
4. **Fine-tune** ML models for your use case
5. **Deploy** to production with proper environment setup

---

**Backend Version:** 2.0  
**Last Updated:** April 11, 2024  
**Status:** ✅ COMPLETE AND PRODUCTION-READY
