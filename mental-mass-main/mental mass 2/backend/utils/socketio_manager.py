"""
Socket.IO manager for real-time events
This module stores the socketio instance for use across the app
"""

socketio = None


def init_socketio(socketio_instance):
    """Initialize the socketio instance"""
    global socketio
    socketio = socketio_instance


def get_socketio():
    """Get the socketio instance"""
    return socketio


def emit_dashboard_update(data):
    """Emit dashboard update to all connected clients"""
    if socketio:
        socketio.emit("dashboard_update", data)
        print(f"[SOCKETIO] Dashboard update emitted: {data.get('emotion', 'unknown')}")


def emit_session_created(session_data):
    """Emit when a new session is created"""
    if socketio:
        socketio.emit("session_created", session_data)
        print(f"[SOCKETIO] Session created event emitted")


def emit_emotion_detected(emotion_data):
    """Emit when emotion is detected"""
    if socketio:
        socketio.emit("emotion_detected", emotion_data)
        print(f"[SOCKETIO] Emotion detected: {emotion_data.get('emotion', 'unknown')}")
