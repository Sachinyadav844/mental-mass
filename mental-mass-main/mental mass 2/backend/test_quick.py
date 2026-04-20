#!/usr/bin/env python
"""Quick test to show complete analysis flow"""

import requests
import base64
import json

print("\n" + "="*75)
print("EMOTION DETECTION - QUICK TEST")
print("="*75 + "\n")

# Login
print("Step 1: Authenticate")
print("-" * 75)

response = requests.post('http://localhost:5000/login', json={
    'email': 'test@gmail.com',
    'password': '123456'
}, timeout=10)

if response.status_code != 200:
    print(f"✗ Login failed: {response.status_code}")
    exit(1)

token = response.json().get('token')
print(f"✓ Authenticated")
print(f"  Token: {token[:35]}...\n")

# Create and analyze test image
print("Step 2: Create and Analyze Test Image")
print("-" * 75)

try:
    import cv2
    import numpy as np
    
    # Create a proper face-like image
    img = np.ones((200, 200, 3), dtype=np.uint8) * 180
    cv2.circle(img, (100, 100), 80, (210, 170, 140), -1)  # Face (skin tone)
    cv2.circle(img, (75, 80), 10, (50, 50, 50), -1)        # Left eye
    cv2.circle(img, (125, 80), 10, (50, 50, 50), -1)       # Right eye
    cv2.ellipse(img, (100, 130), (25, 15), 0, 0, 180, (50, 50, 50), 2)  # Smile
    
    path = 'quick_test.jpg'
    cv2.imwrite(path, img)
    print(f"✓ Image created: {path} (200x200 pixels)")
    
except Exception as e:
    print(f"✗ Image creation failed: {e}")
    exit(1)

# Test both upload methods
headers = {'Authorization': f'Bearer {token}'}
url = 'http://localhost:5000/analyze_face'

print("\nAnalyzing with FILE UPLOAD method...")
print("-" * 75)

try:
    with open(path, 'rb') as f:
        response = requests.post(url, files={'image': f}, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ API Response (File Upload):")
        print(f"  Status: {response.status_code} OK")
        print(f"  Success: {result.get('success')}")
        print(f"  Emotion: {result.get('emotion')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Method: {result.get('method')}")
        print(f"  Raw Response:\n{json.dumps(result, indent=2)}")
    else:
        print(f"✗ API Error: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"✗ Request failed: {e}")

print("\nAnalyzing with BASE64 JSON method...")
print("-" * 75)

try:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(url, json={
        'image': f'data:image/jpeg;base64,{b64}',
        'webcam': False
    }, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ API Response (Base64):")
        print(f"  Status: {response.status_code} OK")
        print(f"  Success: {result.get('success')}")
        print(f"  Emotion: {result.get('emotion')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Method: {result.get('method')}")
        print(f"  Raw Response:\n{json.dumps(result, indent=2)}")
    else:
        print(f"✗ API Error: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"✗ Request failed: {e}")

# Cleanup
import os
try:
    os.remove(path)
    print(f"\n✓ Cleanup complete")
except:
    pass

print("\n" + "="*75)
print("TEST COMPLETE")
print("="*75 + "\n")
