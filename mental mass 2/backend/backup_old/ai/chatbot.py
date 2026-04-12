import os
import random
import re

OPENAI_AVAILABLE = False
openai = None

try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SYSTEM_PROMPT = (
    "You are a supportive mental health companion focused on wellness and emotional support. "
    "Provide empathetic, positive, and safe suggestions for managing stress, anxiety, mood, and daily mental health. "
    "Never provide medical diagnoses, treatment plans, or emergency advice. "
    "Keep responses brief (2-3 sentences), kind, and actionable. "
    "Focus on coping strategies, self-care, mindfulness, and positive psychology. "
    "If someone seems in crisis, gently suggest professional help. "
    "Always end with encouragement."
)

FALLBACK_PATTERNS = {
    'stress': 'Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8. This can help activate your relaxation response and reduce tension.',
    'anxious': 'Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. This mindfulness exercise can help bring you back to the present moment.',
    'sad': 'Consider a small act of self-kindness today, like listening to a favorite song or taking a warm shower. Small steps can help shift your mood gently.',
    'tired': 'Prioritize rest by setting a consistent bedtime routine. Even 10 minutes of deep breathing before sleep can improve your rest quality.',
    'angry': 'Step back and practice the STOP technique: Stop, Take a breath, Observe your thoughts, Proceed mindfully. This creates space between stimulus and response.',
    'lonely': 'Reach out to someone you trust with a simple message. Connection, even brief, can help ease feelings of isolation.',
    'overwhelmed': 'Break tasks into tiny steps and focus on just one thing at a time. Celebrate completing each small step.',
    'happy': 'Savor this positive moment by noting what feels good. Positive emotions are worth acknowledging and remembering.',
    'fear': 'Remember that fear often feels bigger than it is. Try writing down your worries and then identifying one small action you can take.',
    'confused': 'When feeling unclear, try a short walk or change of scenery. Sometimes movement helps clarify thoughts.',
    'grateful': 'Gratitude can be a powerful mood booster. Try noting three things you appreciate right now.',
    'motivated': 'Channel this energy into one meaningful action. Small, consistent steps build momentum.'
}


def _sanitize_message(message):
    if not isinstance(message, str):
        return ''
    return re.sub(r'[^\w\s\.,!?\'-]', '', message).strip()


def _openai_response(message):
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        return None
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message}
            ],
            temperature=0.7,
            max_tokens=150,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        reply = response.choices[0].message.content.strip()
        # Ensure response is appropriate
        if len(reply) > 500 or any(word in reply.lower() for word in ['diagnosis', 'treatment', 'medication']):
            return None
        return reply
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


def _fallback_response(message):
    if not message:
        return 'I am here to listen and support you. How are you feeling today?'

    lower = message.lower()

    # Check for crisis indicators
    crisis_words = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'emergency']
    if any(word in lower for word in crisis_words):
        return 'I am concerned about what you are sharing. Please reach out to a crisis hotline immediately (988 in the US) or emergency services. You are not alone, and help is available right now.'

    # Check for specific emotional states
    for keyword, reply in FALLBACK_PATTERNS.items():
        if keyword in lower:
            return reply

    # General supportive responses
    if any(word in lower for word in ['help', 'support', 'advice']):
        return 'I am here to support you. Try taking a few deep breaths and sharing what is on your mind. Small steps can make a big difference.'

    if any(word in lower for word in ['thank', 'thanks', 'appreciate']):
        return 'You are welcome. Remember that taking care of your mental health is an act of strength. Keep going.'

    # Default supportive response
    return (
        'Thank you for sharing that with me. Emotions can be complex, and it is brave to acknowledge them. '
        'Consider a gentle activity like deep breathing or a short walk. You are taking positive steps by being here.'
    )


def generate_chat_response(message, user_id=None, history=None):
    message = _sanitize_message(message)
    if not message:
        return 'Please share a little more about how you are feeling so I can support you.'

    response = _openai_response(message)
    if response:
        return response

    return _fallback_response(message)
