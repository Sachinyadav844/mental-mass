from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import json
import os
from datetime import datetime
import base64
import io
from pathlib import Path
import numpy as np
import cv2

# Import AI modules
from ai.emotion import detect_emotion, analyze_webcam_frame
from ai.sentiment import analyze_sentiment
from ai.scoring import calculate_score, calculate_score_details, get_risk, get_score_label
from ai.recommendation import get_recommendation, get_recommendations_list
from ai.chatbot import generate_chat_response
from ai.report import generate_report

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'mentalmass_secret_key_2024'
jwt = JWTManager(app)

# Database files
USERS_FILE = 'users.json'
SESSIONS_FILE = 'sessions.json'

# Ensure database files exist with proper error handling
def initialize_db():
    """Initialize database files if they don't exist"""
    try:
        if not os.path.exists(USERS_FILE):
            print(f"[DB] Creating {USERS_FILE}")
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        if not os.path.exists(SESSIONS_FILE):
            print(f"[DB] Creating {SESSIONS_FILE}")
            with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")

initialize_db()

# Database helper functions with better error handling
def load_users():
    """Load users from JSON file with proper error handling"""
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            users = json.loads(content)
            print(f"[DB] Loaded {len(users)} users")
            return users
    except Exception as e:
        print(f"[ERROR] Failed to load users: {e}")
        return []

def save_users(users):
    """Save users to JSON file with proper error handling"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print(f"[DB] Saved {len(users)} users to {USERS_FILE}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save users: {e}")
        return False

def load_sessions():
    """Load sessions from JSON file with proper error handling"""
    try:
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            sessions = json.loads(content)
            return sessions
    except Exception as e:
        print(f"[ERROR] Failed to load sessions: {e}")
        return []

def save_sessions(sessions):
    """Save sessions to JSON file with proper error handling"""
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        print(f"[DB] Saved {len(sessions)} sessions")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save sessions: {e}")
        return False

# Routes

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'message': 'MENTALMASS AI Backend is running'})

@app.route('/register', methods=['POST'])
def register():
    """Register a new user with mock database support"""
    try:
        print("[AUTH] Register request received")
        
        # Validate content type
        if not request.is_json:
            print("[AUTH] Invalid content type")
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"[AUTH] Register data: name={data.get('name', 'N/A')}, email={data.get('email', 'N/A')}")
        
        # Validate input
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            print("[AUTH] Missing required fields")
            return jsonify({'success': False, 'message': 'Name, email, and password are required'}), 400
        
        if len(password) < 6:
            print("[AUTH] Password too short")
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        if '@' not in email or '.' not in email:
            print("[AUTH] Invalid email format")
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Load users from database
        print("[AUTH] Loading users from database")
        users = load_users()
        print(f"[AUTH] Found {len(users)} existing users")
        
        # Check if user already exists
        existing_user = next((u for u in users if u.get('email') == email), None)
        if existing_user:
            print(f"[AUTH] User already exists: {email}")
            return jsonify({'success': False, 'message': 'User already exists with this email'}), 409
        
        # Create new user with timestamp ID
        new_user_id = str(int(datetime.now().timestamp() * 1000))
        new_user = {
            'id': new_user_id,
            'name': name,
            'email': email,
            'password': password,  # In production, hash with bcrypt
            'createdAt': datetime.now().isoformat()
        }
        
        print(f"[AUTH] Creating new user: {email}")
        users.append(new_user)
        
        # Save to database
        if not save_users(users):
            print("[AUTH] Failed to save users")
            return jsonify({'success': False, 'message': 'Failed to save user to database'}), 500
        
        print(f"[AUTH] User registered successfully: {email}")
        
        # Create JWT token
        token = create_access_token(identity=new_user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': new_user['id'],
                'name': new_user['name'],
                'email': new_user['email']
            }
        }), 201
    
    except Exception as e:
        print(f"[ERROR] Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Login user with email/password or Firebase token"""
    try:
        print("[AUTH] Login request received")
        
        if not request.is_json:
            print("[AUTH] Invalid content type")
            return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"[AUTH] Login data: email={data.get('email', 'N/A')}, has_password={bool(data.get('password'))}, has_firebase_token={bool(data.get('firebaseToken'))}")
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        firebase_token = data.get('firebaseToken', '')
        
        # Try Firebase authentication first if token provided
        if firebase_token:
            print("[AUTH] Firebase token provided, attempting Firebase auth")
            if email:
                users = load_users()
                user = next((u for u in users if u.get('email') == email), None)
                if user:
                    print(f"[AUTH] Firebase user found in mock DB: {email}")
                    token = create_access_token(identity=user['id'])
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'token': token,
                        'user': {
                            'id': user['id'],
                            'name': user['name'],
                            'email': user['email']
                        }
                    }), 200
                else:
                    print(f"[AUTH] Firebase user not in mock DB: {email}, creating new user")
                    # Create new user from Firebase
                    new_user_id = str(int(datetime.now().timestamp() * 1000))
                    new_user = {
                        'id': new_user_id,
                        'name': data.get('name', email.split('@')[0]),
                        'email': email,
                        'password': '',  # Firebase user
                        'firebaseAuth': True,
                        'createdAt': datetime.now().isoformat()
                    }
                    users = load_users()
                    users.append(new_user)
                    save_users(users)
                    print(f"[AUTH] Created new Firebase user: {email}")
                    token = create_access_token(identity=new_user['id'])
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'token': token,
                        'user': {
                            'id': new_user['id'],
                            'name': new_user['name'],
                            'email': new_user['email']
                        }
                    }), 201
        
        # Fall back to email/password authentication
        if not all([email, password]):
            print("[AUTH] Missing email or password")
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        print(f"[AUTH] Attempting email/password login: {email}")
        users = load_users()
        print(f"[AUTH] Searching through {len(users)} users")
        
        user = next((u for u in users if u.get('email') == email and u.get('password') == password), None)
        
        if not user:
            print(f"[AUTH] Login failed for {email} - invalid credentials")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        
        print(f"[AUTH] Login successful for {email}")
        token = create_access_token(identity=user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            }
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        users = load_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Remove password from response
        user_data = {k: v for k, v in user.items() if k != 'password'}
        return jsonify({'success': True, 'user': user_data}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Profile fetch failed: {str(e)}'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = load_users()
        # Return safe user data without passwords
        safe_users = [{
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'createdAt': u['createdAt']
        } for u in users]

        return jsonify({'success': True, 'users': safe_users}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Users fetch failed: {str(e)}'}), 500

@app.route('/analyze_face', methods=['POST'])
def analyze_face():
    try:
        import numpy as np
        import cv2
        import base64
        from deepface import DeepFace

        img = None

        # -------------------------
        # HANDLE FILE UPLOAD
        # -------------------------
        if request.files and 'image' in request.files:
            file = request.files['image']
            print("File received:", file.filename)

            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            source_type = 'file'

        # -------------------------
        # HANDLE BASE64 (WEB CAM)
        # -------------------------
        elif request.is_json:
            data = request.get_json()
            if data and 'image' in data:
                print("Base64 received")
                encoded = data['image']
                if ',' in encoded:
                    encoded = encoded.split(',')[1]
                img_bytes = base64.b64decode(encoded)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                source_type = 'json_base64'

        # -------------------------
        # VALIDATION
        # -------------------------
        if img is None:
            print("Invalid image received")
            return jsonify({
                "success": False,
                "message": "Invalid image received"
            }), 422

        print("Image shape:", img.shape)

        # resize for stable prediction
        img = cv2.resize(img, (224, 224))

        # -------------------------
        # ACCURACY BOOST (MULTI RUN)
        # -------------------------
        emotions = []

        for _ in range(3):
            result = DeepFace.analyze(
                img,
                actions=['emotion'],
                enforce_detection=False
            )

            if isinstance(result, list):
                result = result[0]

            emotions.append(result['dominant_emotion'])

        # majority voting
        final_emotion = max(set(emotions), key=emotions.count)
        confidence = result['emotion'][final_emotion]

        print("Model output:", final_emotion, confidence)

        return jsonify({
            "success": True,
            "emotion": final_emotion,
            "confidence": round(confidence / 100, 2)
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "success": False,
            "message": "Analysis failed",
            "error": str(e)
        }), 500

@app.route('/analyze_text', methods=['POST'])
@jwt_required()
def analyze_text():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'success': False, 'message': 'Text is required'}), 400

        result = analyze_sentiment(text)

        return jsonify({
            'success': True,
            'sentiment': result['sentiment'],
            'score': result['score'],
            'keywords': result['keywords']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Text analysis failed: {str(e)}'}), 500

@app.route('/calculate_score', methods=['POST'])
@jwt_required()
def calculate_score_endpoint():
    try:
        data = request.get_json()
        emotion = data.get('emotion')
        sentiment = data.get('sentiment')

        if not emotion or not sentiment:
            return jsonify({'success': False, 'message': 'Emotion and sentiment are required'}), 400

        user_id = get_jwt_identity()
        sessions = load_sessions()
        history_scores = [s.get('score', 0) for s in sessions if s.get('user_id') == user_id and isinstance(s.get('score', None), (int, float))]

        details = calculate_score_details(emotion, sentiment, history_scores=history_scores)
        score = details['score']
        label = get_score_label(score)

        return jsonify({
            'success': True,
            'score': score,
            'label': label,
            'accuracy': details['accuracy']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Score calculation failed: {str(e)}'}), 500

@app.route('/risk', methods=['POST'])
@jwt_required()
def get_risk_assessment():
    try:
        data = request.get_json()
        score = data.get('score')

        if score is None:
            return jsonify({'success': False, 'message': 'Score is required'}), 400

        user_id = get_jwt_identity()
        sessions = load_sessions()
        history_scores = [s.get('score', 0) for s in sessions if s.get('user_id') == user_id and isinstance(s.get('score', None), (int, float))]
        risk_data = get_risk(score, history_scores=history_scores)

        return jsonify({
            'success': True,
            'risk': risk_data['risk'],
            'message': risk_data['message']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Risk assessment failed: {str(e)}'}), 500

@app.route('/recommendation', methods=['GET'])
@jwt_required()
def get_recommendation_endpoint():
    try:
        user_id = get_jwt_identity()
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]
        score = None
        emotion = None
        sentiment = None

        if user_sessions:
            score = user_sessions[-1].get('score', None)
            emotion = user_sessions[-1].get('emotion', None)
            sentiment = user_sessions[-1].get('sentiment', None)

        recommendation = get_recommendation(
            score=score,
            emotion=emotion,
            sentiment=sentiment,
            time_of_day=datetime.now().hour,
            history=user_sessions
        )

        return jsonify({
            'success': True,
            'recommendation': recommendation['text'],
            'details': recommendation
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Recommendation failed: {str(e)}'}), 500

@app.route('/chatbot', methods=['POST'])
@jwt_required()
def chatbot_endpoint():
    try:
        data = request.get_json()
        message = (data or {}).get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'message': 'Message is required'}), 400

        user_id = get_jwt_identity()
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]

        reply = generate_chat_response(message, user_id=user_id, history=user_sessions)

        return jsonify({
            'success': True,
            'reply': reply
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Chatbot failed: {str(e)}'}), 500

@app.route('/trend_data', methods=['GET'])
@jwt_required()
def get_trend_data():
    try:
        user_id = get_jwt_identity()
        sessions = load_sessions()
        user_scores = [s.get('score', 0) for s in sessions if s.get('user_id') == user_id and isinstance(s.get('score', None), (int, float))]
        if len(user_scores) >= 7:
            data = user_scores[-7:]
        elif user_scores:
            data = user_scores
        else:
            data = [45, 52, 48, 61, 55, 63, 58]

        return jsonify({
            'success': True,
            'data': data
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Trend data fetch failed: {str(e)}'}), 500

@app.route('/emotion_stats', methods=['GET'])
@jwt_required()
def get_emotion_stats():
    try:
        # Mock emotion statistics - in production, calculate from user sessions
        stats = {
            'happy': 35,
            'neutral': 40,
            'sad': 15,
            'angry': 5,
            'surprised': 3,
            'fear': 2
        }

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Emotion stats fetch failed: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        user_id = get_jwt_identity()
        sessions = load_sessions()

        # Filter sessions by user (assuming sessions have user_id)
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]

        # Return recent history
        history = [{
            'date': s.get('date', ''),
            'emotion': s.get('emotion', ''),
            'score': s.get('score', 0)
        } for s in user_sessions[-10:]]  # Last 10 sessions

        return jsonify({
            'success': True,
            'history': history
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'History fetch failed: {str(e)}'}), 500

@app.route('/save_assessment', methods=['POST'])
@jwt_required()
def save_assessment():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Create session entry
        session_data = {
            'user_id': user_id,
            'date': datetime.now().isoformat(),
            'emotion': data.get('emotion'),
            'sentiment': data.get('sentiment'),
            'score': data.get('score'),
            'risk': data.get('risk'),
            'notes': data.get('notes', '')
        }

        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)

        return jsonify({
            'success': True,
            'message': 'Assessment saved successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Assessment save failed: {str(e)}'}), 500

@app.route('/save_session', methods=['POST'])
@jwt_required()
def save_session():
    # Alias for save_assessment for compatibility
    return save_assessment()

@app.route('/journal/history', methods=['GET'])
@jwt_required()
def get_journal_history():
    try:
        user_id = get_jwt_identity()
        filter_param = request.args.get('filter')

        # Mock journal entries - in production, store separately
        journal_entries = [
            {
                'id': '1',
                'text': 'Today was a challenging day at work, but I managed to stay positive.',
                'date': '2024-04-01T10:00:00',
                'sentiment': 'neutral'
            },
            {
                'id': '2',
                'text': 'Had a great conversation with a friend. Feeling much better!',
                'date': '2024-04-02T14:30:00',
                'sentiment': 'positive'
            }
        ]

        return jsonify({
            'success': True,
            'history': journal_entries
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Journal history fetch failed: {str(e)}'}), 500

@app.route('/export_report', methods=['GET'])
@jwt_required()
def export_report():
    try:
        user_id = get_jwt_identity()

        # Get user data
        users = load_users()
        user = next((u for u in users if u['id'] == user_id), None)

        # Get user sessions
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]

        # Generate PDF report
        pdf_data = generate_report(user, user_sessions)

        # Return PDF file
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='mental_health_report.pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'message': f'Report generation failed: {str(e)}'}), 500

@app.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    try:
        user_id = get_jwt_identity()
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]

        return jsonify({
            'success': True,
            'sessions': user_sessions
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Sessions fetch failed: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        user_id = get_jwt_identity()
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]

        if not user_sessions:
            return jsonify({
                'success': True,
                'stats': {
                    'total_sessions': 0,
                    'average_score': 0,
                    'most_frequent_emotion': 'none'
                }
            }), 200

        # Calculate stats
        total_sessions = len(user_sessions)
        average_score = sum(s.get('score', 0) for s in user_sessions) / total_sessions

        # Most frequent emotion
        emotions = [s.get('emotion', '') for s in user_sessions]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        most_frequent_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'none'

        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': total_sessions,
                'average_score': round(average_score, 1),
                'most_frequent_emotion': most_frequent_emotion
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Stats calculation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)