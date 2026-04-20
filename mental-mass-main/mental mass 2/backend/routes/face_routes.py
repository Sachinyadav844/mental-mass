"""
Face analysis routes
Handles POST /analyze_face endpoint
"""
from flask import Blueprint, request, jsonify
from utils.error_handler import error_response, success_response, ImageProcessingError, MLModelError
from utils.logger import log_access, log_error
from utils.socketio_manager import emit_emotion_detected
from utils.image_utils import load_image_from_file, load_image_from_base64, validate_image_dimensions
from ml.emotion_detector import analyze_emotion
from ml.sentiment_analyzer import is_sentiment_available
from ml.face_validator import validate_face_detected
import json
import concurrent.futures
import time

face_bp = Blueprint('face', __name__)

# ThreadPoolExecutor for async processing (VERY IMPORTANT)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


@face_bp.route('/analyze_face', methods=['POST'])
def analyze_face():
    """
    Analyze facial emotion from image or webcam

    Accepts:
        - multipart/form-data with 'image' file
        - JSON with 'image_data' (base64-encoded string)

    Returns:
        {
            emotion: string,
            confidence: float (0-1),
            all_emotions: dict,
            face_detected: bool,
            face_box: {x, y, width, height},
            passes: int
        }
    """
    try:
        log_access('/analyze_face', 'POST')
        print('[FACE] Request received', 'files=', bool(request.files), 'json=', request.is_json)
        print('[FACE] request.files keys=', list(request.files.keys()))
        print('[FACE] request.json=', request.get_json(silent=True))

        # =====================================================================
        # LOAD IMAGE
        # =====================================================================
        img = None
        source_type = None

        # Try file upload first
        if request.files and 'image' in request.files:
            try:
                img = load_image_from_file(request.files['image'])
                source_type = 'file'
                print("[FACE] Image loaded from file upload")
            except ImageProcessingError as e:
                return error_response(e)

        # Try base64 JSON
        elif request.is_json:
            data = request.get_json(silent=True)
            print('[FACE] JSON payload data=', data)
            # Support both 'image_data' and 'image' keys for base64
            image_data = data.get('image_data') or (data.get('image') if data else None)
            if image_data:
                try:
                    img = load_image_from_base64(image_data)
                    source_type = 'webcam'
                    print("[FACE] Image loaded from base64")
                except ImageProcessingError as e:
                    return error_response(e)

        # No image provided
        if img is None:
            return error_response(
                ImageProcessingError(
                    'No image provided',
                    'Provide either multipart file with key "image" or JSON with key "image" or "image_data"'
                )
            )

        # =====================================================================
        # VALIDATE IMAGE
        # =====================================================================
        try:
            validate_image_dimensions(img)
        except ImageProcessingError as e:
            return error_response(e)

        print("[FACE] Image received")
        print("[FACE] Processing started")

        # =====================================================================
        # ANALYZE EMOTION (ASYNC THREADING)
        # =====================================================================
        try:
            # Submit to thread pool for non-blocking execution
            future = executor.submit(run_emotion_analysis, img)

            # Wait for result with timeout (25 seconds)
            emotion_result = future.result(timeout=25)

            print("[FACE] Processing completed")

        except concurrent.futures.TimeoutError:
            print("[FACE] Processing timeout - returning safe response")
            return error_response(
                MLModelError(
                    'Processing taking longer than expected',
                    'Please try again or use a different image'
                ),
                408  # Request Timeout
            )
        except (ImageProcessingError, MLModelError) as e:
            return error_response(e)

        # =====================================================================
        # RETURN RESPONSE
        # =====================================================================
        response_data = {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'all_emotions': emotion_result['all_emotions'],
            'face_detected': emotion_result['face_detected'],
            'face_box': emotion_result['face_box'],
            'passes': emotion_result['passes'],
            'source': source_type
        }

        # Emit real-time emotion detection event
        emit_emotion_detected({
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'face_detected': emotion_result['face_detected'],
            'timestamp': time.time()
        })

        return success_response(response_data)

    except Exception as e:
        log_error('FACE_ANALYSIS_ERROR', str(e))
        return error_response(MLModelError(f'Face analysis error: {str(e)}'), 500)


def run_emotion_analysis(img):
    """
    Run emotion analysis in separate thread
    """
    return analyze_emotion(img)


@face_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    from ml.ai_config import deepface_available, sentiment_available, chatbot_available

    return success_response({
        'emotion_detection': deepface_available,
        'sentiment': sentiment_available,
        'chatbot': chatbot_available
    })
