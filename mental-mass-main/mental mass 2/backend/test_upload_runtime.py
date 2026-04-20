import requests
from pathlib import Path
from PIL import Image, ImageDraw

url = 'http://127.0.0.1:5000'
print('Checking server...')
try:
    r = requests.get(url, timeout=5)
    print('Health status:', r.status_code)
    print('Health response:', r.text)
except Exception as e:
    raise SystemExit(f'Server not reachable: {e}')

print('Logging in...')
login = requests.post(url + '/login', json={'email': 'test@gmail.com', 'password': '123456'}, timeout=10)
print('Login status:', login.status_code)
print(login.text)
if login.status_code != 200:
    raise SystemExit('Login failed')
token = login.json().get('token')
headers = {'Authorization': f'Bearer {token}'}

path = Path('backend/test_upload_image.jpg')
img = Image.new('RGB', (240, 240), (240, 220, 200))
d = ImageDraw.Draw(img)
d.ellipse((40, 40, 200, 200), fill=(255, 210, 180), outline=(120, 70, 40), width=4)
d.ellipse((85, 95, 105, 115), fill=(20, 20, 20))
d.ellipse((145, 95, 165, 115), fill=(20, 20, 20))
d.arc((90, 120, 170, 180), 0, 180, fill=(20, 20, 20), width=4)
img.save(path)
print('Created test image at', path)

with open(path, 'rb') as f:
    files = {'image': f}
    r = requests.post(url + '/analyze_face', files=files, headers=headers, timeout=30)
    print('Analyze status:', r.status_code)
    print('Analyze response:', r.text)

path.unlink()
print('Cleaned up test image')
