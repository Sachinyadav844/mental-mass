from pathlib import Path

emotion_text = '''import base64
import random
from collections import Counter

import cv2
import numpy as np

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception as e:
    DEEPFACE_AVAILABLE = False
    print(f"[AI] DeepFace not available ({e}), using fallback strategies")

FER_AVAILABLE = False
fer_detector = None


def load_fer_detector():
    global FER_AVAILABLE, fer_detector
    if fer_detector is not None:
        return
    try:
        from fer import FER
        fer_detector = FER(mtcnn=True)
        FER_AVAILABLE = True
        print("[AI] FER detector loaded successfully")
    except Exception as e:
        FER_AVAILABLE = False
        print(f"[AI] FER not available ({e}), using uncertain fallback")


_face_cascade = None

def get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        try:
            _face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if _face_cascade.empty():
                print("[AI] Haarcascade loaded but empty")
        except Exception as e:
            print(f"[AI] Failed to load Haarcascade: {e}")
    return _face_cascade


def detect_emotion(image_input):
    try:
        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            raise ValueError('Invalid image input')

        if img is None or img.size == 0:
            raise ValueError('Invalid image data')

        return _analyze_image_for_emotion(img, num_iterations=3)
    except Exception as e:
        print(f"[EMOTION] Error in detect_emotion: {e}")
        return _uncertain_emotion()


def analyze_webcam_frame(base64_image):
    try:
        if not base64_image:
            raise ValueError('No webcam image provided')

        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None or img.size == 0:
            raise ValueError('Failed to decode webcam image')

        return _analyze_image_for_emotion(img, num_iterations=1, enforce_detection=False)
    except Exception as e:
        print(f"[WEBCAM] Error processing frame: {e}")
        return _uncertain_emotion()


def _analyze_image_for_emotion(img, num_iterations=3, enforce_detection=True):
    try:
        if img is None or img.shape[0] == 0 or img.shape[1] == 0:
            print('[EMOTION] Invalid image dimensions')
            return _uncertain_emotion()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = get_face_cascade()
        if face_cascade is None or face_cascade.empty():
            print('[EMOTION] Face cascade unavailable')
            return _uncertain_emotion()

        faces = _detect_faces(gray)
        print(f'[EMOTION] Faces detected: {len(faces)}')

        face_img = _select_face_roi(img, faces)
        if face_img is None:
            print('[EMOTION] No face ROI detected, using full image fallback')
            face_img = img

        if DEEPFACE_AVAILABLE:
            result = _run_deepface_ensemble(face_img, num_iterations, enforce_detection=enforce_detection)
            if result and result['confidence'] >= 0.6:
                result['method'] = 'ensemble'
                return result

            fallback = _run_deepface_ensemble(img, max(1, num_iterations - 1), enforce_detection=False)
            if fallback and fallback['confidence'] >= 0.6:
                fallback['method'] = 'ensemble'
                fallback['model'] = 'deepface_full'
                return fallback

        fer_result = _run_fer_fallback(img)
        if fer_result and fer_result.get('confidence', 0) >= 0.5:
            return fer_result

        if DEEPFACE_AVAILABLE:
            print('[EMOTION] DeepFace available but confidence below threshold, returning uncertain result')
            return _uncertain_emotion()

        return _mock_emotion_analysis(img)
    except Exception as e:
        print(f'[EMOTION] Critical error in analysis: {e}')
        return _uncertain_emotion()


def _detect_faces(gray):
    face_cascade = get_face_cascade()
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    if len(faces) == 0:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(20, 20), flags=cv2.CASCADE_SCALE_IMAGE)
    if len(faces) == 0:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(15, 15), flags=cv2.CASCADE_SCALE_IMAGE)
    return faces


def _select_face_roi(img, faces):
    if len(faces) == 0:
        return None
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = largest_face
    padding = max(int(w * 0.2), 10)
    x_start = max(0, x - padding)
    y_start = max(0, y - padding)
    x_end = min(img.shape[1], x + w + padding)
    y_end = min(img.shape[0], y + h + padding)
    face_roi = img[y_start:y_end, x_start:x_end]
    return face_roi if face_roi.size else None


def _run_deepface_ensemble(img, num_iterations=3, enforce_detection=True):
    if not DEEPFACE_AVAILABLE:
        return None

    emotions = []
    confidences = []

    for i in range(num_iterations):
        try:
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = DeepFace.analyze(
                rgb_img,
                actions=['emotion'],
                enforce_detection=enforce_detection
            )
            output = result[0] if isinstance(result, list) else result
            dominant = _normalize_emotion(output.get('dominant_emotion', 'neutral'))
            scores = output.get('emotion', {})
            confidence = max(scores.values()) / 100.0 if scores else 0.5
            emotions.append(dominant)
            confidences.append(confidence)
            print(f'[EMOTION] DeepFace iteration {i+1}: {dominant} ({confidence:.2f})')
        except Exception as e:
            print(f'[EMOTION] DeepFace iteration {i+1} failed: {e}')
            continue

    if not emotions:
        return None

    chosen = Counter(emotions).most_common(1)[0][0]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    return {
        'emotion': chosen,
        'confidence': round(avg_confidence, 2),
        'model': 'deepface',
        'votes': dict(Counter(emotions))
    }


def _run_fer_fallback(img):
    load_fer_detector()
    if not FER_AVAILABLE or fer_detector is None:
        return None

    try:
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detections = fer_detector.detect_emotions(rgb_img)
        if not detections:
            return None
        detection = max(detections, key=lambda d: d.get('box', [0, 0, 0, 0])[2] * d.get('box', [0, 0, 0, 0])[3])
        emotions = detection.get('emotions', {})
        if not emotions:
            return None
        dominant = max(emotions, key=emotions.get)
        confidence = emotions.get(dominant, 0) / 100.0
        return {
            'emotion': _normalize_emotion(dominant),
            'confidence': round(min(max(confidence, 0.0), 1.0), 2),
            'method': 'fer_fallback'
        }
    except Exception as e:
        print(f'[EMOTION] FER fallback failed: {e}')
        return None


def _normalize_emotion(emotion):
    if not emotion:
        return 'neutral'
    normalized = str(emotion).lower().strip()
    if normalized in ['happy', 'joy', 'joyful', 'smile']:
        return 'happy'
    if normalized in ['surprise', 'surprised', 'amazed']:
        return 'surprised'
    if normalized in ['sad', 'sadness', 'down']:
        return 'sad'
    if normalized in ['angry', 'anger']:
        return 'angry'
    if normalized in ['fear', 'scared', 'anxious', 'anxiety']:
        return 'fear'
    if normalized in ['disgust', 'disappointed']:
        return 'disgust'
    if normalized in ['neutral', 'calm', 'bored']:
        return 'neutral'
    return normalized


def _mock_emotion_analysis(img=None):
    if img is not None and img.size:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
    else:
        brightness = 120

    if brightness > 150:
        return {'emotion': 'happy', 'confidence': 0.7, 'method': 'mock', 'details': 'bright image fallback'}
    if brightness < 100:
        return {'emotion': 'neutral', 'confidence': 0.55, 'method': 'mock', 'details': 'dark image fallback'}
    return {'emotion': 'neutral', 'confidence': 0.6, 'method': 'mock', 'details': 'balanced image fallback'}


def _uncertain_emotion():
    return {
        'emotion': 'uncertain',
        'confidence': 0.45,
        'method': 'low_confidence'
    }
'''

Path('backend/ai/emotion.py').write_text(emotion_text, encoding='utf-8')
