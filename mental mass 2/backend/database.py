"""
Database initialization and management for MentalMass
Uses SQLite with SQLAlchemy ORM
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
from config import DB_PATH, DB_URI
import json

# Create SQLAlchemy base
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    """User account model"""
    __tablename__ = 'users'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    firebase_auth = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Session(Base):
    """Analysis session model"""
    __tablename__ = 'sessions'
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Emotion & Sentiment
    emotion = Column(String(50))
    emotion_confidence = Column(Float)
    all_emotions = Column(Text)  # JSON serialized
    
    sentiment = Column(String(50))
    sentiment_confidence = Column(Float)
    sentiment_keywords = Column(Text)  # JSON serialized
    
    # Mood Score
    mood_score = Column(Float)
    risk_level = Column(String(50))
    risk_color = Column(String(50))
    
    # Face Detection
    face_detected = Column(Boolean)
    face_box = Column(Text)  # JSON serialized: {x, y, w, h}
    
    # User Self Score
    self_score = Column(Integer)
    
    # Metadata
    image_source = Column(String(50))  # 'file', 'webcam', 'text_only'
    
    def __repr__(self):
        return f'<Session {self.id} - {self.emotion}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'emotion': self.emotion,
            'emotion_confidence': self.emotion_confidence,
            'all_emotions': json.loads(self.all_emotions) if self.all_emotions else {},
            'sentiment': self.sentiment,
            'sentiment_confidence': self.sentiment_confidence,
            'sentiment_keywords': json.loads(self.sentiment_keywords) if self.sentiment_keywords else [],
            'mood_score': self.mood_score,
            'risk_level': self.risk_level,
            'risk_color': self.risk_color,
            'face_detected': self.face_detected,
            'face_box': json.loads(self.face_box) if self.face_box else None,
            'self_score': self.self_score,
            'image_source': self.image_source,
        }


class Assessment(Base):
    """Self-assessment questionnaire response"""
    __tablename__ = 'assessments'
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    answers = Column(Text)  # JSON serialized array of scores
    total_score = Column(Integer)
    risk_level = Column(String(50))
    
    def __repr__(self):
        return f'<Assessment {self.id}>'


# ============================================================================
# DATABASE SETUP
# ============================================================================

engine = None
SessionLocal = None


def init_db():
    """Initialize database with all tables"""
    global engine, SessionLocal
    
    # Create engine
    engine = create_engine(
        DB_URI,
        echo=False,
        connect_args={'check_same_thread': False}  # Allow concurrent access
    )
    
    # Enable WAL mode for concurrent reads
    if 'sqlite' in str(DB_URI):
        try:
            with engine.connect() as conn:
                conn.execute(text('PRAGMA journal_mode=WAL'))
                conn.execute(text('PRAGMA synchronous=NORMAL'))
                conn.commit()
        except Exception as e:
            print(f"[DB] Warning: Could not set PRAGMA: {str(e)}")

    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Setup session factory
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    
    print(f"[DB] Database initialized at {DB_PATH}")
    return engine, SessionLocal


def get_session():
    """Get database session"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()


def close_session(session):
    """Close database session"""
    if session:
        session.close()


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def create_user(user_id, name, email, password, firebase_auth=False):
    """Create new user"""
    session = get_session()
    try:
        user = User(
            id=user_id,
            name=name,
            email=email,
            firebase_auth=firebase_auth
        )
        if not firebase_auth:
            user.set_password(password)
        
        session.add(user)
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session(session)


def get_user_by_email(email):
    """Get user by email"""
    session = get_session()
    try:
        return session.query(User).filter(User.email == email).first()
    finally:
        close_session(session)


def get_user_by_id(user_id):
    """Get user by ID"""
    session = get_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        close_session(session)


def save_session_data(session_data):
    """Save analysis session to database"""
    session = get_session()
    try:
        db_session = Session(**session_data)
        session.add(db_session)
        session.commit()
        return db_session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session(session)


def get_user_sessions(user_id, limit=30):
    """Get user's recent sessions"""
    session = get_session()
    try:
        sessions = session.query(Session)\
            .filter(Session.user_id == user_id)\
            .order_by(Session.timestamp.desc())\
            .limit(limit)\
            .all()
        return [s.to_dict() for s in reversed(sessions)]
    finally:
        close_session(session)


def get_session_stats(user_id):
    """Get aggregate statistics for user's sessions"""
    session = get_session()
    try:
        sessions = session.query(Session)\
            .filter(Session.user_id == user_id)\
            .all()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'avg_mood_score': 0,
                'emotion_distribution': {},
                'risk_distribution': {},
                'weekly_average': [],
            }
        
        # Calculate stats
        total = len(sessions)
        avg_score = sum(s.mood_score for s in sessions if s.mood_score) / total
        
        # Emotion distribution
        emotion_dist = {}
        for s in sessions:
            if s.emotion:
                emotion_dist[s.emotion] = emotion_dist.get(s.emotion, 0) + 1
        
        # Risk distribution
        risk_dist = {}
        for s in sessions:
            if s.risk_level:
                risk_dist[s.risk_level] = risk_dist.get(s.risk_level, 0) + 1
        
        return {
            'total_sessions': total,
            'avg_mood_score': round(avg_score, 2),
            'emotion_distribution': emotion_dist,
            'risk_distribution': risk_dist,
            'last_session': sessions[-1].to_dict() if sessions else None,
        }
    finally:
        close_session(session)


def save_assessment(assessment_data):
    """Save assessment response"""
    session = get_session()
    try:
        db_assessment = Assessment(**assessment_data)
        session.add(db_assessment)
        session.commit()
        return db_assessment
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session(session)
