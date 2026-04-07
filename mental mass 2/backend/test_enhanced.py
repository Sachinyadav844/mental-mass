#!/usr/bin/env python
"""Enhanced emotion detection test with detailed logging"""

import requests
import base64
import os
import json
from pathlib import Path

print("="*80)
print("EMOTION DETECTION TEST SUITE")
print("="*80)

# First, let's check what files we have
print("\n[STEP 1] Checking available test files...\n")

backend_path = Path('.')
print(f"Current directory: {backend_path.resolve()}")
print(f"\nFiles in backend directory:")
for item in backend_path.glob('*'):
    if item.is_file():
        size = item.stat().st_size
        print(f"  ✓ {item.name:<30} ({size:>8} bytes)")

# Step 2: Create a better test image with OpenCV
print("\n[STEP 2] Creating test image with OpenCV...\n")

try:
    import cv2
    import numpy as np
    
    # Create a synthetic face using filled rectangles and circles
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200  # Light background
    
    # Draw face outline (circle)
    cv2.circle(img, (320, 240), 150, (200, 150, 100), -1)  # Skin tone
    cv2.circle(img, (320, 240), 150, (100, 100, 100), 3)
    
    # Draw eyes
    cv2.circle(img, (270, 200), 20, (50, 50, 50), -1)  # Left eye
    cv2.circle(img, (370, 200), 20, (50, 50, 50), -1)  # Right eye
    cv2.circle(img, (275, 195), 8, (255, 255, 255), -1)  # Left pupil
    cv2.circle(img, (375, 195), 8, (255, 255, 255), -1)  # Right pupil
    
    # Draw nose
    pts = np.array([[320, 220], [310, 250], [330, 250]], np.int32)
    cv2.polylines(img, [pts], False, (100, 100, 100), 2)
    
    # Draw mouth (happy smile)
    cv2.ellipse(img, (320, 280), (50, 30), 0, 0, 180, (50, 50, 50), 2)
    
    test_image_path = 'test_synthetic_face.jpg'
    cv2.imwrite(test_image_path, img)
    print(f"✓ Synthetic face created: {test_image_path}")
    print(f"  Dimensions: {img.shape[1]}x{img.shape[0]} (width x height)")
    print(f"  Size: {os.path.getsize(test_image_path)} bytes")
    
except Exception as e:
    print(f"✗ Failed to create image: {e}")
    print("\n  Falling back to minimal JPEG...")
    
    # Fallback: minimal valid JPEG
    test_image_path = 'test_minimal.jpg'
    minimal_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdeghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00\x00\xff\xd9'
    with open(test_image_path, 'wb') as f:
        f.write(minimal_jpeg)
    print(f"✓ Fallback JPEG created: {test_image_path}")

# Step 3: Authenticate
print("\n[STEP 3] Authenticating with backend...\n")

login_url = 'http://localhost:5000/login'
login_data = {
    'email': 'test@gmail.com',
    'password': '123456'
}

try:
    response = requests.post(login_url, json=login_data, timeout=10)
    if response.status_code != 200:
        print(f"✗ Authentication failed!")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        exit(1)
    
    result = response.json()
    token = result.get('token')
    user = result.get('user', {})
    
    print(f"✓ Authentication successful!")
    print(f"  User: {user.get('name')} ({user.get('email')})")
    print(f"  Token: {token[:30]}...")
    
except Exception as e:
    print(f"✗ Authentication error: {e}")
    exit(1)

# Step 4: Test file upload
print("\n[STEP 4] Testing file upload analysis...\n")

if not os.path.exists(test_image_path):
    print(f"✗ Test image not found: {test_image_path}")
    exit(1)

analyze_url = 'http://localhost:5000/analyze_face'
headers = {'Authorization': f'Bearer {token}'}

try:
    file_size = os.path.getsize(test_image_path)
    print(f"Uploading: {test_image_path} ({file_size} bytes)")
    
    with open(test_image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(
            analyze_url,
            files=files,
            headers=headers,
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ File upload successful!")
        print(f""\
"  ╔════════════════════════════════╗")
        print(f"  ║ EMOTION ANALYSIS RESULT         ║")
        print(f"  ╠════════════════════════════════╣")
        print(f"  ║ Emotion    : {result.get('emotion', 'N/A'):<21} ║")
        print(f"  ║ Confidence : {result.get('confidence', 'N/A'):<20} ║")
        print(f"  ║ Method     : {result.get('method', 'N/A'):<21} ║")
        if 'details' in result:
            detail_str = str(result['details'])[:20]
            print(f"  ║ Details    : {detail_str:<21} ║")
        print(f"  ╚════════════════════════════════╝")
    else:
        print(f"✗ Upload failed!")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"✗ Upload error: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Test base64 upload
print("\n[STEP 5] Testing base64 upload analysis...\n")

try:
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"Base64 image size: {len(image_data)} bytes")
    
    payload = {
        'image': f'data:image/jpeg;base64,{image_data}',
        'webcam': False
    }
    
    response = requests.post(
        analyze_url,
        json=payload,
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Base64 upload successful!")
        print(f""\
"  ╔════════════════════════════════╗")
        print(f"  ║ EMOTION ANALYSIS RESULT         ║")
        print(f"  ╠════════════════════════════════╣")
        print(f"  ║ Emotion    : {result.get('emotion', 'N/A'):<21} ║")
        print(f"  ║ Confidence : {result.get('confidence', 'N/A'):<20} ║")
        print(f"  ║ Method     : {result.get('method', 'N/A'):<21} ║")
        if 'iterations' in result:
            print(f"  ║ Iterations : {result.get('iterations'):<21} ║")
        print(f"  ╚════════════════════════════════╝")
    else:
        print(f"✗ Base64 upload failed!")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"✗ Base64 upload error: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\n[CLEANUP] Removing test files...\n")

for file_pattern in ['test_*.jpg', 'test_*.jpeg', 'temp_face.*']:
    import glob
    for file in glob.glob(file_pattern):
        try:
            os.remove(file)
            print(f"✓ Removed: {file}")
        except:
            pass

print("\n" + "="*80)
print("TEST SUITE COMPLETE")
print("="*80)
