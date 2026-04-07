#!/usr/bin/env python
"""Integration test for webcam emotion detection"""

import requests
import json
import base64

def test_integration():
    print('[TEST] Starting integration test...')
    
    # Test 1: Login
    login_url = 'http://localhost:5000/login'
    login_data = {
        'email': 'test@gmail.com',
        'password': '123456'
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=5)
        if response.status_code != 200:
            print(f'[TEST] Login failed: {response.status_code}')
            return False
        
        token = response.json().get('token')
        print(f'[TEST] ✓ Login successful')
        
        # Test 2: Webcam emotion analysis with base64
        analyze_url = 'http://localhost:5000/analyze_face'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Create a minimal valid JPEG image
        minimal_jpeg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
            b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
            b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00'
            b'\x01\x00\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01'
            b'\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06'
            b'\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03'
            b'\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A'
            b'\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br'
            b'\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdeghij'
            b'stuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98'
            b'\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7'
            b'\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6'
            b'\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3'
            b'\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x00'
            b'\x00\xff\xd9'
        )
        
        base64_image = 'data:image/jpeg;base64,' + base64.b64encode(minimal_jpeg).decode('utf-8')
        
        payload = {
            'image': base64_image,
            'webcam': True
        }
        
        response = requests.post(analyze_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print('[TEST] ✓ Emotion analysis successful')
            print(f'       Emotion: {result.get("emotion")}')
            print(f'       Confidence: {result.get("confidence")}')
            print(f'       Method: {result.get("method")}')
            return True
        else:
            print(f'[TEST] Emotion analysis returned {response.status_code}')
            print(f'       Response: {response.text}')
            return False
    
    except Exception as e:
        print(f'[TEST] Error: {e}')
        print('[TEST] Make sure backend is running on http://localhost:5000')
        return False

if __name__ == '__main__':
    test_integration()
