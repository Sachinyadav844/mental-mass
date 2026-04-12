"""
Image processing utilities for MentalMass
"""
import base64
import io
import cv2
import numpy as np
from werkzeug.datastructures import FileStorage
from config import (
    IMAGE_RESIZE_WIDTH, IMAGE_RESIZE_HEIGHT,
    IMAGE_BLUR_KERNEL, ALLOWED_IMAGE_EXTENSIONS
)
from utils.error_handler import ImageProcessingError


# ============================================================================
# IMAGE LOADING
# ============================================================================

def load_image_from_file(file_obj):
    """
    Load image from FileStorage object
    
    Args:
        file_obj: werkzeug FileStorage object
    
    Returns:
        numpy array (BGR image)
    
    Raises:
        ImageProcessingError
    """
    try:
        if not isinstance(file_obj, FileStorage):
            raise ImageProcessingError('Invalid file object')
        
        # Check file extension
        filename = file_obj.filename or ''
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ImageProcessingError(
                f'Invalid file extension: {ext}. Allowed: {ALLOWED_IMAGE_EXTENSIONS}',
                f'Attempted to upload {ext} file'
            )
        
        # Read file bytes
        file_bytes = np.frombuffer(file_obj.read(), np.uint8)
        
        # Decode image
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None or img.size == 0:
            raise ImageProcessingError('Failed to decode image file')
        
        return img
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to load image from file: {str(e)}')


def load_image_from_base64(base64_string):
    """
    Load image from base64-encoded string (typically from webcam)
    
    Args:
        base64_string: Base64-encoded image string (may include data URI prefix)
    
    Returns:
        numpy array (BGR image)
    
    Raises:
        ImageProcessingError
    """
    try:
        if not base64_string or not isinstance(base64_string, str):
            raise ImageProcessingError('Invalid base64 string')
        
        # Strip data URI prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        try:
            img_bytes = base64.b64decode(base64_string)
        except Exception as e:
            raise ImageProcessingError(f'Failed to decode base64: {str(e)}')
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None or img.size == 0:
            raise ImageProcessingError('Failed to decode base64 image')
        
        return img
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to load image from base64: {str(e)}')


# ============================================================================
# IMAGE PREPROCESSING
# ============================================================================

def preprocess_image(img):
    """
    Preprocess image for ML analysis
    
    Pipeline:
    1. Resize to 224x224
    2. Convert BGR to RGB
    3. Equalize histogram for brightness normalization
    4. Apply Gaussian blur for noise reduction
    
    Args:
        img: numpy array (BGR image)
    
    Returns:
        Preprocessed numpy array
    
    Raises:
        ImageProcessingError
    """
    try:
        if img is None or img.size == 0:
            raise ImageProcessingError('Empty image')
        
        # 1. Resize
        img = cv2.resize(img, (IMAGE_RESIZE_WIDTH, IMAGE_RESIZE_HEIGHT))
        
        # 2. Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 3. Equalize histogram (only on grayscale)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # 4. Apply Gaussian blur for noise reduction
        img = cv2.GaussianBlur(img, IMAGE_BLUR_KERNEL, 0)
        
        return img
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to preprocess image: {str(e)}')


def convert_to_bgr(img):
    """
    Convert RGB image back to BGR for OpenCV compatibility
    
    Args:
        img: numpy array (RGB image)
    
    Returns:
        numpy array (BGR image)
    """
    try:
        if img.ndim != 3 or img.shape[2] != 3:
            raise ImageProcessingError('Invalid image dimensions')
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to convert image format: {str(e)}')


# ============================================================================
# IMAGE VALIDATION
# ============================================================================

def validate_image_dimensions(img, min_width=50, min_height=50):
    """
    Validate image has minimum dimensions
    
    Args:
        img: numpy array
        min_width: minimum width in pixels
        min_height: minimum height in pixels
    
    Returns:
        True if valid, raises exception otherwise
    
    Raises:
        ImageProcessingError
    """
    try:
        if img is None or img.size == 0:
            raise ImageProcessingError('Empty image')
        
        height, width = img.shape[:2]
        
        if width < min_width or height < min_height:
            raise ImageProcessingError(
                f'Image too small: {width}x{height}. Minimum: {min_width}x{min_height}'
            )
        
        return True
    
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f'Failed to validate image: {str(e)}')


# ============================================================================
# IMAGE CLEANUP
# ============================================================================

def cleanup_image_memory(img):
    """
    Release image memory
    
    Args:
        img: numpy array
    """
    try:
        if img is not None:
            del img
    except Exception:
        pass


# ============================================================================
# IMAGE FORMAT CONVERSION
# ============================================================================

def image_to_base64(img):
    """
    Convert image to base64 string
    
    Args:
        img: numpy array
    
    Returns:
        Base64-encoded string with data URI prefix
    """
    try:
        _, buffer = cv2.imencode('.jpg', img)
        img_bytes = buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f'data:image/jpeg;base64,{img_base64}'
    except Exception as e:
        raise ImageProcessingError(f'Failed to convert image to base64: {str(e)}')


def get_image_info(img):
    """
    Get image metadata
    
    Args:
        img: numpy array
    
    Returns:
        Dictionary with image info
    """
    try:
        if img is None:
            return None
        
        height, width = img.shape[:2]
        channels = img.shape[2] if len(img.shape) > 2 else 1
        
        return {
            'width': int(width),
            'height': int(height),
            'channels': int(channels),
            'dtype': str(img.dtype),
            'size_mb': float(img.nbytes / (1024 * 1024))
        }
    except Exception as e:
        raise ImageProcessingError(f'Failed to get image info: {str(e)}')
