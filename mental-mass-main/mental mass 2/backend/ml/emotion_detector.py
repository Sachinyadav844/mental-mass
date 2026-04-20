"""
Facial emotion: OpenCV face detect + crop, then DeepFace (Emotion).
Falls back to neutral when DeepFace is unavailable or all passes fail.
"""
import os
import tempfile
import threading

import cv2
import numpy as np

from utils.image_utils import validate_image_dimensions
from utils.error_handler import MLModelError, ImageProcessingError
from config import DEEPFACE_NUM_PASSES, EMOTION_NUMERIC_MAP

import ml.ai_config as ai_config

DeepFace = None
DEEPFACE_ERROR = None


def initialize_deepface():
    """
    Load TensorFlow + DeepFace once at startup; update ai_config flags.
    TF_USE_LEGACY_KERAS must be set in app.py before this module is imported.
    """
    global DeepFace, DEEPFACE_ERROR
    try:
        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
        import tensorflow as tf  # noqa: F401 — ensure TF loads before deepface

        _ = tf  # silence lint
        from deepface import DeepFace as _DeepFace

        DeepFace = _DeepFace
        ai_config.deepface_available = True
        ai_config.emotion_model = None
        ai_config.deepface_error = None
        DEEPFACE_ERROR = None
        print("[EMOTION] DeepFace initialized successfully")
    except Exception as e:
        print(f"Error details: {e}")
        DeepFace = None
        DEEPFACE_ERROR = str(e)
        ai_config.deepface_available = False
        ai_config.emotion_model = None
        ai_config.deepface_error = str(e)
        print("[EMOTION] DeepFace unavailable; OpenCV fallback only")

_model_lock = threading.Lock()

EMOTION_MAP = {
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "fear": "fear",
    "surprise": "surprised",
    "surprised": "surprised",
    "disgust": "disgust",
    "neutral": "neutral",
    "uncertain": "uncertain",
}


def is_deepface_available():
    return ai_config.deepface_available


def is_emotion_detection_available():
    """OpenCV + rule fallback always allows a response; DeepFace optional."""
    return True


def get_emotion_detection_status():
    return {
        "deepface_available": ai_config.deepface_available,
        "deepface_error": DEEPFACE_ERROR,
        "primary_model": "DeepFace" if ai_config.deepface_available else "fallback",
    }


def _face_crop_to_temp_jpg(face_bgr):
    """Write cropped face BGR image to a temp file for DeepFace.analyze(img_path=...)."""
    ok, buf = cv2.imencode(".jpg", face_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise MLModelError("Failed to encode face image for analysis")
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        tmp.write(buf.tobytes())
        tmp.flush()
        path = tmp.name
    finally:
        tmp.close()
    return path


def _analyze_deepface_file(img_path, num_passes):
    # Import DeepFace if available
    if not ai_config.deepface_available:
        raise MLModelError("DeepFace not available")

    try:
        from deepface import DeepFace as _DeepFace

        DeepFace_cls = _DeepFace
    except ImportError as e:
        print(f"Error details: {e}")
        raise MLModelError("DeepFace import failed")

    emotion_results = []
    kwargs = {
        "img_path": img_path,
        "actions": ["emotion"],
        "enforce_detection": False,
    }
    if ai_config.emotion_model is not None:
        kwargs["models"] = {"emotion": ai_config.emotion_model}

    with _model_lock:
        for pass_num in range(num_passes):
            try:
                result = DeepFace_cls.analyze(**kwargs)
                if isinstance(result, list):
                    result = result[0]
                emotion_results.append(result)
                dom = result.get("dominant_emotion", "neutral")
                raw = (result.get("emotion") or {}).get(dom, 0)
                print(f"[EMOTION] DeepFace pass {pass_num + 1}/{num_passes} - {dom} ({raw})")
            except Exception as e:
                print(f"[EMOTION] DeepFace pass {pass_num + 1} failed: {e}")
                print(f"Error details: {e}")

    if not emotion_results:
        raise MLModelError("All DeepFace passes failed")
    return emotion_results


def _aggregate_emotion_results(results, face_box, num_passes, model_name):
    all_emotions = {}
    dominant_emotions = []

    for result in results:
        emotions = result.get("emotion") or {}
        dominant = result.get("dominant_emotion", "neutral")
        dominant_emotions.append(str(dominant).lower())
        for emotion, score in emotions.items():
            ek = str(emotion).lower()
            all_emotions.setdefault(ek, []).append(float(score))

    averaged_emotions = {
        emotion: round(float(np.mean(scores)), 2) for emotion, scores in all_emotions.items()
    }

    from collections import Counter

    dominant_emotion = Counter(dominant_emotions).most_common(1)[0][0]
    de = str(dominant_emotion).lower()
    emotion_out = EMOTION_MAP.get(de, de)
    allowed = {"happy", "sad", "angry", "fear", "surprised", "disgust", "neutral", "uncertain"}
    if emotion_out not in allowed:
        emotion_out = "neutral"

    raw_conf = float(averaged_emotions.get(dominant_emotion, averaged_emotions.get(de, 0)))
    confidence_norm = raw_conf / 100.0 if raw_conf > 1.0 else raw_conf

    if confidence_norm < 0.25:
        emotion_out = "neutral"
        confidence_norm = max(confidence_norm, 0.0)

    return _create_emotion_response(
        {
            "emotion": emotion_out,
            "confidence": confidence_norm,
            "all_emotions": averaged_emotions,
        },
        face_box,
        num_passes,
        model_name,
    )


def _create_emotion_response(emotion_data, face_box, num_passes, model_name):
    emotion = emotion_data["emotion"]
    confidence = float(emotion_data["confidence"])
    all_emotions = emotion_data.get("all_emotions", {})

    if confidence > 1:
        confidence = round(confidence / 100.0, 4)
    else:
        confidence = round(confidence, 4)

    norm_all = {}
    for k, v in all_emotions.items():
        fv = float(v)
        norm_all[k] = round(fv / 100.0, 4) if fv > 1 else round(fv, 4)

    return {
        "emotion": emotion,
        "confidence": confidence,
        "all_emotions": norm_all,
        "face_detected": True,
        "face_box": face_box,
        "passes": num_passes,
        "model": model_name,
        "emotion_numeric": EMOTION_NUMERIC_MAP.get(emotion, EMOTION_NUMERIC_MAP.get("neutral", 60)),
    }


def analyze_emotion(img, num_passes=None, enforce_detection=None):
    """
    OpenCV face detection -> crop -> DeepFace multi-inference with majority voting.
    If confidence < 0.5, return uncertain. Falls back to neutral when DeepFace unavailable.
    """
    num_passes = num_passes or DEEPFACE_NUM_PASSES
    enforce_detection = enforce_detection if enforce_detection is not None else False

    try:
        validate_image_dimensions(img)

        # Enhanced OpenCV face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            # No face detected - return neutral with low confidence
            print("[EMOTION] No face detected - returning neutral")
            return _create_emotion_response(
                {
                    "emotion": "neutral",
                    "confidence": 0.3,
                    "all_emotions": {
                        "angry": 0.0,
                        "disgust": 0.0,
                        "fear": 0.0,
                        "happy": 0.0,
                        "sad": 0.0,
                        "surprise": 0.0,
                        "neutral": 0.3,
                    },
                },
                {"x": 0, "y": 0, "width": 0, "height": 0},
                num_passes,
                "no_face_detected",
            )

        # Use the largest face
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        (x, y, w, h) = faces[0]

        # Crop and resize face
        face_roi = img[y:y+h, x:x+w]
        face_resized = cv2.resize(face_roi, (224, 224))

        face_box = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}

        tmp_path = None
        try:
            tmp_path = _face_crop_to_temp_jpg(face_resized)
            if ai_config.deepface_available:
                emotion_results = _analyze_deepface_file(tmp_path, num_passes)
                result = _aggregate_emotion_results(emotion_results, face_box, num_passes, "DeepFace")

                # Check confidence threshold
                if result["confidence"] < 0.5:
                    result["emotion"] = "uncertain"
                    result["confidence"] = 0.3

                print(f"[EMOTION] Final result: emotion={result['emotion']}, confidence={result['confidence']}")
                return result
        except (MLModelError, Exception) as e:
            print(f"[EMOTION] DeepFace path failed: {e}")
            print(f"Error details: {e}")
        finally:
            if tmp_path and os.path.isfile(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        print("[EMOTION] Using neutral fallback (DeepFace unavailable or failed).")
        result = _create_emotion_response(
            {
                "emotion": "neutral",
                "confidence": 0.25,
                "all_emotions": {
                    "angry": 0.0,
                    "disgust": 0.0,
                    "fear": 0.0,
                    "happy": 0.0,
                    "sad": 0.0,
                    "surprise": 0.0,
                    "neutral": 1.0,
                },
            },
            face_box,
            num_passes,
            "fallback",
        )
        print(f"[EMOTION] Fallback result: emotion={result['emotion']}, confidence={result['confidence']}")
        return result

    except (ImageProcessingError, MLModelError):
        raise
    except Exception as e:
        print(f"[EMOTION] Unexpected error: {e}")
        print(f"Error details: {e}")
        # Return safe neutral response on any error
        return _create_emotion_response(
            {
                "emotion": "neutral",
                "confidence": 0.25,
                "all_emotions": {
                    "angry": 0.0,
                    "disgust": 0.0,
                    "fear": 0.0,
                    "happy": 0.0,
                    "sad": 0.0,
                    "surprise": 0.0,
                    "neutral": 1.0,
                },
            },
            {"x": 0, "y": 0, "width": 0, "height": 0},
            num_passes,
            "error_fallback",
        )
