# ⚡ SOCKET.IO QUICK START GUIDE

## 30-Second Setup

### Terminal 1 - Backend
```bash
cd "e:\mental mass 2\mental mass 2\backend"
pip install -r requirements.txt
python app.py
```

Wait for: `[APP] Socket.IO enabled for real-time updates`

### Terminal 2 - Frontend
```bash
cd "e:\mental mass 2\mental mass 2\frontend"
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## ✅ Verify It Works

1. Open Dashboard page
2. Check browser console (F12)
3. Should see:
   ```
   [Socket] Connected successfully
   [Socket] Subscribed to event: dashboard_update
   ```

4. Open another tab, perform analysis (emotion/sentiment)
5. Return to Dashboard tab
6. **Should update automatically** ✨
7. Toast notification appears
8. Charts refresh with new data

---

## 🔄 Real-Time Flow

```
User runs analysis
    ↓
Backend emits Socket event
    ↓
All connected Dashboards receive update
    ↓
Charts update automatically
    ↓
Toast notification shown
```

---

## 🛠️ What Was Changed

### Backend
- ✅ `requirements.txt` - Added flask-socketio, eventlet
- ✅ `app.py` - SocketIO initialization
- ✅ `utils/socketio_manager.py` - NEW event management
- ✅ Routes - Added real-time event emission

### Frontend
- ✅ `package.json` - Added socket.io-client
- ✅ `hooks/useSocket.ts` - NEW Socket hook
- ✅ `pages/Dashboard.tsx` - Real-time listeners

---

## 📊 Features

✅ Auto-refresh (no manual refresh needed)
✅ Real-time events (emotion, sentiment, sessions)
✅ Auto-reconnect (5 retry attempts)
✅ Toast notifications (new sessions)
✅ Dynamic chart updates
✅ Error handling with fallbacks

---

## 🚨 Troubleshooting

| Issue | Fix |
|-------|-----|
| Not connecting | Check port 5000, restart both |
| Import error | `npm install` & `pip install -r requirements.txt` |
| Dashboard not updating | Check WebSocket in DevTools Network tab |
| Port in use | Kill: `netstat -tulpn \| grep 5000` |

---

## ✅ Success Checklist

- [ ] Backend starts with "[APP] Socket.IO enabled"
- [ ] Frontend starts without errors
- [ ] Browser console shows "[Socket] Connected successfully"
- [ ] Perform analysis in one tab
- [ ] Dashboard updates automatically in other tab
- [ ] Toast notification appears
- [ ] Charts refresh with new data

---

## 🎯 Complete!

Your real-time dashboard is ready. Perform analysis and watch updates happen automatically! ✨
