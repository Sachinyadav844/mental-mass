"""
Face detection and validation using OpenCV Haar cascades
"""
import cv2
import numpy as np
from utils.error_handler import NoFaceDetectedError, ImageProcessingError


# Global face cascade
_face_cascade = None


def get_face_cascade():
    """
    Load Haar cascade for face detection
    
    Returns:
        CascadeClassifier object
    
    Raises:
        ImageProcessingError
    """
    global _face_cascade
    
    if _face_cascade is not None:
        return _face_cascade
    
    try:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        _face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if _face_cascade.empty():
            raise ImageProcessingError('Failed to load Haar cascade classifier')
        
        print(f"[FACE_VALIDATOR] Haar cascade loaded from {cascade_path}")
        return _face_cascade
    
    except Exception as e:
        raise ImageProcessingError(f'Failed to initialize face cascade: {str(e)}')


def detect_faces(img, scale_factor=1.1, min_neighbors=5, min_size=(30, 30)):
    """
    Detect faces in image using Haar cascade
    
    Args:
        img: numpy array (BGR image)
        scale_factor: Image pyramid scale factor
        min_neighbors: Minimum neighbors to retain detection
        min_size: Minimum face size
    
    Returns:
        List of face rectangles (x, y, w, h)
    
    Raises:
        ImageProcessingError
    """
    try:
        if img is None or img.size == 0:
            raise ImageProcessingError('Empty image')
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Get cascade
        cascade = get_face_cascade()
        
        # Detect faces
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Face detection failed: {str(e)}')


def validate_face_detected(img):
    """
    Validate that at least one face is detected in image
    
    Args:
        img: numpy array (BGR image)
    
    Returns:
        Dictionary with face info or raises exception
    
    Raises:
        NoFaceDetectedError
    """
    try:
        faces = detect_faces(img)
        
        if len(faces) == 0:
            raise NoFaceDetectedError('No faces detected in the image')
        
        # Get largest face (assume main subject)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        return {
            'detected': True,
            'count': len(faces),
            'main_face': {
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h),
                'area': int(w * h)
            },
            'all_faces': [
                {'x': int(rect[0]), 'y': int(rect[1]), 'width': int(rect[2]), 'height': int(rect[3])}
                for rect in faces
            ]
        }
    
    except NoFaceDetectedError:
        raise
    except Exception as e:
        raise NoFaceDetectedError(f'Face validation failed: {str(e)}')


def extract_face_region(img, face_rect):
    """
    Extract face region from image
    
    Args:
        img: numpy array (BGR image)
        face_rect: tuple (x, y, w, h)
    
    Returns:
        Face region as numpy array
    
    Raises:
        ImageProcessingError
    """
    try:
        x, y, w, h = face_rect
        
        # Add padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2*padding)
        h = min(img.shape[0] - y, h + 2*padding)
        
        face_img = img[y:y+h, x:x+w]
        
        if face_img.size == 0:
            raise ImageProcessingError('Failed to extract face region')
        
        return face_img
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to extract face: {str(e)}')


def draw_face_box(img, face_rect, color=(0, 255, 0), thickness=2):
    """
    Draw face bounding box on image (for debugging)
    
    Args:
        img: numpy array (BGR image)
        face_rect: tuple (x, y, w, h)
        color: RGB color tuple
        thickness: line thickness
    
    Returns:
        Image with drawn box
    """
    try:
        x, y, w, h = face_rect
        img_copy = img.copy()
        cv2.rectangle(img_copy, (x, y), (x+w, y+h), color, thickness)
        return img_copy
    except Exception:
        return img
