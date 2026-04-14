# Socket.IO Real-Time Dashboard Implementation Guide

## ✅ COMPLETED CHANGES

### 1. Backend - Socket.IO Setup

#### 1.1 Updated `backend/requirements.txt`
- ✅ Added `flask-socketio>=5.3.0`
- ✅ Added `python-socketio>=5.9.0`
- ✅ Added `python-engineio>=4.7.0`
- ✅ Added `eventlet>=0.33.0`

#### 1.2 Updated `backend/app.py`
- ✅ Imported `SocketIO` from `flask_socketio`
- ✅ Created `socketio = SocketIO(app, cors_allowed_origins="*")`
- ✅ Initialized socketio_manager with `init_socketio(socketio)`
- ✅ Replaced `app.run()` with `socketio.run()` for event handling

#### 1.3 Created `backend/utils/socketio_manager.py`
- ✅ Centralized Socket.IO management
- ✅ `init_socketio()` - Initialize socketio instance
- ✅ `emit_dashboard_update()` - Broadcast dashboard updates
- ✅ `emit_session_created()` - Broadcast when new session created
- ✅ `emit_emotion_detected()` - Broadcast emotion detection
- ✅ `get_socketio()` - Access socketio instance from routes

#### 1.4 Updated Backend Routes

**`backend/routes/session_routes.py`**
- ✅ Import `emit_dashboard_update`, `emit_session_created`
- ✅ Emit real-time events when sessions are created
- ✅ Sends: emotion, sentiment, mood_score, risk_level, timestamp

**`backend/routes/face_routes.py`**
- ✅ Import `emit_emotion_detected`
- ✅ Emit emotion detection events immediately after analysis
- ✅ Sends: emotion, confidence, face_detected, timestamp

**`backend/routes/text_routes.py`**
- ✅ Import `emit_dashboard_update`
- ✅ Emit sentiment analysis events
- ✅ Sends: sentiment, confidence, timestamp

### 2. Frontend - Socket.IO Setup

#### 2.1 Updated `frontend/package.json`
- ✅ Added `socket.io-client: ^4.7.2`

#### 2.2 Created `frontend/src/hooks/useSocket.ts`
- ✅ `useSocket()` hook for individual component connections
- ✅ `useGlobalSocket()` hook for global singleton connection
- ✅ `initGlobalSocket()` for centralized socket management
- ✅ Event handlers: connect, disconnect, error, connect_error
- ✅ Methods: connect, on, off, emit, isConnected

#### 2.3 Updated `frontend/src/pages/Dashboard.tsx`
- ✅ Import `useGlobalSocket` hook
- ✅ Initialize socket connection on component mount
- ✅ Listen to `dashboard_update` events
- ✅ Listen to `session_created` events
- ✅ Listen to `emotion_detected` events
- ✅ Auto-refresh dashboard on real-time updates
- ✅ Show toast notifications for new sessions
- ✅ Improved error handling with specific error messages
- ✅ Better fallback UI when no sessions available

### 3. Features Implemented

#### Real-Time Updates
✅ Dashboard auto-updates when new analysis is performed
✅ No page refresh required
✅ Automatic reconnection with exponential backoff
✅ Toast notifications for new sessions
✅ Chart updates happen automatically

#### Event Types
✅ `dashboard_update` - Main analytics update
✅ `session_created` - New session created
✅ `emotion_detected` - Emotion analysis complete
✅ `connect` - Socket connection established
✅ `disconnect` - Socket connection lost
✅ `error` - Connection error
✅ `connect_error` - Connection failed

#### Connection Features
✅ WebSocket + polling fallback
✅ Automatic reconnection (5 retries)
✅ Configurable delays (1-5 seconds)
✅ CORS enabled for cross-origin
✅ Preserves connection across page navigation

## 🚀 DEPLOYMENT INSTRUCTIONS

### Backend Setup
```bash
cd "e:\mental mass 2\mental mass 2\backend"

# Install new dependencies
pip install -r requirements.txt

# OR if using specific packages
pip install flask-socketio python-socketio python-engineio eventlet

# Run backend
python app.py
# Will output: "[APP] Socket.IO enabled for real-time updates"
```

### Frontend Setup
```bash
cd "e:\mental mass 2\mental mass 2\frontend"

# Install socket.io-client
npm install socket.io-client

# Or already included in package.json, so just run
npm install

# Start development server
npm run dev
```

## ✅ VALIDATION CHECKLIST

After deployment, verify:

### Backend
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] Backend starts: `[APP] Socket.IO enabled for real-time updates`
- [ ] No import errors related to socketio
- [ ] Backend runs on port 5000
- [ ] CORS enabled for `*` origins

### Frontend
- [ ] `npm install` completes without errors
- [ ] No TypeScript errors in useSocket.ts
- [ ] Dashboard page loads without errors
- [ ] Browser console shows: `[Socket] Connecting to backend`
- [ ] Browser console shows: `[Socket] Connected successfully`

### Connection Testing
- Open Dashboard page
- Open browser DevTools → Console
- Check for these messages:
  - `[Socket] Connecting to backend at http://localhost:5000`
  - `[Socket] Connected successfully`
  - `[Socket] Subscribed to event: dashboard_update`
  - `[Socket] Subscribed to event: session_created`
  - `[Socket] Subscribed to event: emotion_detected`

### Real-Time Updates Testing
1. Keep Dashboard open
2. Open another tab with face/text analysis
3. Perform analysis (emotion detection or sentiment)
4. Return to Dashboard tab
5. Should see:
   - Dashboard updates automatically (no refresh)
   - Toast notification appears for new session
   - Charts update with new data
   - Console shows: `[Dashboard] Received real-time update`

## 📊 Data Flow

```
User performs analysis
    ↓
Backend receives request
    ↓
ML Models process data
    ↓
Backend emits Socket.IO event
    ↓
Frontend receives real-time update
    ↓
Dashboard charts update automatically
    ↓
Toast notification shown to user
```

## 🔧 Troubleshooting

### Socket Connection Fails

**Problem**: `[Socket] Connect error: Error: WebSocket error`

**Solution**:
1. Check backend is running on port 5000
2. Check CORS is enabled in app.py
3. Try refreshing the page
4. Check browser console for specific error

### Real-Time Updates Not Working

**Problem**: Dashboard doesn't update in real-time

**Solution**:
1. Check browser console for `[Socket] Connected successfully`
2. Perform an analysis and check if socket event is emitted
3. Check backend console for: `[SOCKETIO] Dashboard update emitted`
4. Verify network tab shows WebSocket connection in DevTools

### CORS Errors

**Problem**: CORS policy blocking connection

**Solution**: Already fixed - app.py has `cors_allowed_origins="*"`

### Port Already in Use

**Problem**: `Address already in use: ('0.0.0.0', 5000)`

**Solution**:
```bash
# Find process using port 5000
netstat -tulpn | grep 5000

# Kill the process
kill -9 <PID>
```

## 📝 API Endpoints (Unchanged)

All existing endpoints remain unchanged:
- ✅ `GET /sessions` - Get user sessions
- ✅ `POST /sessions` - Create new session
- ✅ `POST /analyze_face` - Emotion analysis
- ✅ `POST /analyze_text` - Sentiment analysis
- ✅ `POST /calculate_score` - Score calculation
- ✅ All other routes unchanged

## 🎯 Key Features

✅ **No Breaking Changes** - All existing APIs work as before
✅ **Backward Compatible** - Old clients still work
✅ **Real-Time Updates** - Dashboard updates automatically
✅ **Automatic Reconnection** - Handles network issues
✅ **Multiple Event Types** - Emotion, sentiment, sessions
✅ **Scalable** - Broadcast to all connected clients
✅ **Error Handling** - Graceful fallbacks

## 📈 Performance

- Socket.IO uses efficient WebSocket protocol
- Fallback to HTTP long-polling if needed
- Minimal bandwidth for small event payloads
- No continuous polling from frontend
- Reduced server load

## 🔒 Security Notes

- CORS enabled for all origins (can be restricted later)
- JWT authentication still required for API endpoints
- Socket.IO events emit to all connected clients
- No authentication-specific event filtering (for now)

## 🚀 Future Improvements

- Add user-specific event namespaces
- Implement room-based updates (per user)
- Add event authentication/validation
- Compress event payloads
- Add rate limiting for events
- Implement event queuing for reliability
