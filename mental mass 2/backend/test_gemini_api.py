import os
from dotenv import load_dotenv
load_dotenv()

print('=== GEMINI API TEST ===')

try:
    import google.generativeai as genai
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Test with a simple mental health query
        test_prompt = """
You are a mental health assistant for a project called MENTALMASS.

RULES:
- Only respond to mental health topics (stress, anxiety, depression, emotions, well-being)
- Do NOT answer coding, tech, or unrelated questions
- If question is unrelated, politely refuse
- Give safe, supportive, and helpful advice
- Do NOT give medical diagnosis
- Keep responses focused on mental wellness

User: I feel stressed about work
"""

        print('Testing Gemini API call...')
        response = model.generate_content(
            test_prompt,
            generation_config={"max_output_tokens": 150, "temperature": 0.7}
        )

        if response.text:
            print('✓ Gemini API working!')
            print('Response:', response.text[:200] + '...')
        else:
            print('✗ Empty response from Gemini')
    else:
        print('✗ No API key found')

except Exception as e:
    print('✗ Gemini test failed:', e)

print('=== TEST COMPLETE ===')