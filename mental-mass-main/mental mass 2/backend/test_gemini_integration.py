import os
from dotenv import load_dotenv
load_dotenv()

print('=== SECURE GEMINI INTEGRATION TEST ===')

# Test .env loading
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print('✓ GEMINI_API_KEY loaded from .env')
    print('  Key starts with:', api_key[:20] + '...')
else:
    print('✗ GEMINI_API_KEY not found')

# Test Gemini import and config
try:
    import google.generativeai as genai
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        print('✓ Gemini API configured successfully')
    else:
        print('✗ Cannot configure Gemini without API key')
except Exception as e:
    print('✗ Gemini configuration failed:', e)

# Test mental health filter
from routes.chatbot_routes import is_mental_health_query

test_queries = [
    ('I feel stressed', True),
    ('How to code in Python?', False),
    ('I am anxious about work', True),
    ('What is the weather?', False),
    ('I feel depressed', True),
    ('Tell me a joke', False)
]

print('\n=== MENTAL HEALTH FILTER TEST ===')
for query, expected in test_queries:
    result = is_mental_health_query(query)
    status = '✓' if result == expected else '✗'
    print(f'{status} "{query}" -> {result} (expected {expected})')

print('\n=== INTEGRATION COMPLETE ===')