#!/usr/bin/env python
"""Comprehensive file upload emotion detection test"""

import requests
import base64
import os
from pathlib import Path

# First, create a sample test image using PIL if available
try:
    from PIL import Image, ImageDraw
    print("[SETUP] Creating test image with PIL...")
    
    # Create a simple image with a white/light background (simulating bright face)
    img = Image.new('RGB', (400, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle (face simulation)
    draw.ellipse([50, 50, 350, 350], fill='#fdbcb4', outline='black', width=2)
    
    # Draw eyes
    draw.ellipse([120, 120, 160, 160], fill='black')
    draw.ellipse([240, 120, 280, 160], fill='black')
    
    # Draw smile for happy expression
    draw.arc([130, 180, 270, 280], 0, 180, fill='black', width=3)
    
    test_image_path = 'test_face_happy.jpg'
    img.save(test_image_path, 'JPEG', quality=95)
    print(f"[SETUP] ✓ Test image created: {test_image_path}")
    print(f"[SETUP] Image size: {img.size[0]}x{img.size[1]} pixels")
    
except ImportError:
    print("[SETUP] PIL not available, generating minimal JPEG manually...")
    # Fallback: create minimal JPEG programmatically
    test_image_path = 'test_face_simple.jpg'
    # Create a simple grayscale JPEG with face-like features
    jpeg_data = bytes([
        0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xff, 0xdb, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0a, 0x0c, 0x14, 0x0d, 0x0c, 0x0b, 0x0b, 0x0c, 0x19, 0x12,
        0x13, 0x0f, 0x14, 0x1d, 0x1a, 0x1f, 0x1e, 0x1d, 0x1a, 0x1c, 0x1c, 0x20,
        0x24, 0x2e, 0x27, 0x20, 0x22, 0x2c, 0x23, 0x1c, 0x1c, 0x28, 0x37, 0x29,
        0x2c, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1f, 0x27, 0x39, 0x3d, 0x38, 0x32,
        0x3c, 0x2e, 0x33, 0x34, 0x32, 0xff, 0xc0, 0x00, 0x0b, 0x08, 0x00, 0x80,
        0x00, 0x80, 0x01, 0x01, 0x11, 0x00, 0xff, 0xc4, 0x00, 0x1f, 0x00, 0x00,
        0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0a, 0x0b,
    ])
    with open(test_image_path, 'wb') as f:
        f.write(jpeg_data)
    print(f"[SETUP] ✓ Minimal test image created: {test_image_path}")

print("\n" + "="*70)
print("EMOTION DETECTION - FILE UPLOAD TEST")
print("="*70 + "\n")

# Step 1: Login to get JWT token
print("[TEST 1] Authenticating...")
login_url = 'http://localhost:5000/login'
login_data = {
    'email': 'test@gmail.com',
    'password': '123456'
}

try:
    response = requests.post(login_url, json=login_data, timeout=10)
    if response.status_code != 200:
        print(f"[ERROR] Login failed: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")
        exit(1)
    
    token = response.json().get('token')
    print(f"[TEST 1] ✓ Authentication successful")
    print(f"         Token: {token[:20]}...")
    
except Exception as e:
    print(f"[ERROR] Login request failed: {e}")
    exit(1)

# Step 2: Test file upload (multipart/form-data)
print("\n[TEST 2] Testing file upload (multipart)...")

if not os.path.exists(test_image_path):
    print(f"[ERROR] Test image not found: {test_image_path}")
    exit(1)

file_size = os.path.getsize(test_image_path)
print(f"         File: {test_image_path}")
print(f"         Size: {file_size} bytes")

analyze_url = 'http://localhost:5000/analyze_face'
headers = {
    'Authorization': f'Bearer {token}'
}

try:
    with open(test_image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(
            analyze_url,
            files=files,
            headers=headers,
            timeout=30
        )
    
    print(f"         Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"[TEST 2] ✓ File upload analysis successful!")
        print(f"\n         RESULTS:")
        print(f"         --------")
        print(f"         Emotion: {result.get('emotion')}")
        print(f"         Confidence: {result.get('confidence')}")
        print(f"         Method: {result.get('method')}")
        if 'iterations' in result:
            print(f"         Iterations: {result.get('iterations')}")
        if 'details' in result:
            print(f"         Details: {result.get('details')}")
    else:
        print(f"[ERROR] File upload failed: {response.status_code}")
        print(f"        Response: {response.text}")

except Exception as e:
    print(f"[ERROR] File upload request failed: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Test base64 image upload
print("\n[TEST 3] Testing base64 image upload...")

try:
    with open(test_image_path, 'rb') as f:
        image_bytes = f.read()
    
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    print(f"         Base64 size: {len(base64_image)} bytes")
    print(f"         First 50 chars: {base64_image[:50]}...")
    
    payload = {
        'image': f'data:image/jpeg;base64,{base64_image}',
        'webcam': False
    }
    
    response = requests.post(
        analyze_url,
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"         Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"[TEST 3] ✓ Base64 upload analysis successful!")
        print(f"\n         RESULTS:")
        print(f"         --------")
        print(f"         Emotion: {result.get('emotion')}")
        print(f"         Confidence: {result.get('confidence')}")
        print(f"         Method: {result.get('method')}")
        if 'iterations' in result:
            print(f"         Iterations: {result.get('iterations')}")
        if 'details' in result:
            print(f"         Details: {result.get('details')}")
    else:
        print(f"[ERROR] Base64 upload failed: {response.status_code}")
        print(f"        Response: {response.text}")

except Exception as e:
    print(f"[ERROR] Base64 upload request failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

# Cleanup
if os.path.exists(test_image_path):
    os.remove(test_image_path)
    print(f"\n[CLEANUP] Removed test image: {test_image_path}")
