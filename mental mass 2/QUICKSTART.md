# MENTALMASS - Complete Setup Guide

## 🚀 Quick Start (Both Frontend & Backend)

### Terminal 1: Start Backend Server

```bash
cd your-project-root
npm run server
```

You should see:
```
Auth server running on http://localhost:5000
Register: POST http://localhost:5000/auth/register
Login: POST http://localhost:5000/auth/login
```

### Terminal 2: Start Frontend (React + Vite)

```bash
cd your-project-root
npm run dev
```

You should see:
```
VITE v5.4.19  ready in 123 ms
➜  Local:   http://localhost:5173/
```

## ✅ Complete System Ready!

- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:5173

---

## 📋 File Structure

```
your-project-root/
│
├── 📁 src/                      # React frontend
│   ├── pages/
│   │   ├── Login.tsx           # Login page
│   │   ├── Register.tsx        # Registration page
│   │   ├── Home.tsx
│   │   └── ...
│   ├── services/
│   │   └── api.ts              # API client (configured for backend)
│   ├── context/
│   │   └── AuthContext.tsx     # Auth state management
│   └── ...
│
├── 📄 server.js                 # Express backend server ⭐
├── 📄 users.json                # Mock database (auto-created)
├── 📄 package.json              # Dependencies
├── 📄 BACKEND_SETUP.md          # Backend documentation
├── 📄 API_TESTS.http            # API test cases
├── 📄 .env.example              # Environment variables template
└── 📄 QUICKSTART.md             # This file
```

---

## 🔐 Authentication Flow

### Registration Flow
```
1. User fills form on /register page
2. Frontend sends POST to http://localhost:5000/auth/register
3. Backend validates input (email format, password strength)
4. Backend checks for duplicate email
5. Backend saves user to users.json
6. Backend returns success + user data
7. Frontend stores token in localStorage
8. Frontend redirects to /dashboard
```

### Login Flow
```
1. User fills form on /login page
2. Frontend sends POST to http://localhost:5000/auth/login
3. Backend validates email & password in users.json
4. Backend returns success + token + user data
5. Frontend stores token in localStorage
6. Frontend sets Authorization header: Bearer <token>
7. Frontend redirects to /dashboard
```

---

## 🧪 Manual Testing

### Option 1: Use REST Client Extension (VS Code)
File: `API_TESTS.http`

1. Install REST Client extension in VS Code
2. Open `API_TESTS.http`
3. Click "Send Request" on any test
4. View response in side panel

### Option 2: Use cURL

```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get Users
curl http://localhost:5000/auth/users
```

### Option 3: Use Postman

1. Open Postman
2. Create collection "MENTALMASS"
3. Add requests:
   - POST `http://localhost:5000/auth/register`
   - POST `http://localhost:5000/auth/login`
   - GET `http://localhost:5000/auth/users`

---

## 📱 Test in Frontend UI

### Using Frontend UI:
1. Navigate to http://localhost:5173/register
2. Fill form: Name, Email, Password
3. Click "Create Account"
4. Should redirect to dashboard (if auth successful)
5. Navigate to http://localhost:5173/login
6. Fill form: Email, Password
7. Click "Sign In"
8. Should access protected pages

---

## 🔍 Troubleshooting

### Issue: CORS Error
**Error**: Access to XMLHttpRequest has been blocked by CORS policy

**Solution**:
- Ensure backend server is running
- Check that `cors()` is enabled in server.js
- Verify baseURL in `src/services/api.ts` is `http://localhost:5000`

### Issue: Port 5000 in use
**Error**: listen EADDRINUSE: address already in use :::5000

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

### Issue: users.json error
**Solution**: Delete `users.json` and restart server (it will auto-create)

### Issue: Network Error
**Error**: Network Error: connect ECONNREFUSED

**Solution**:
- Verify backend is running: `npm run server`
- Verify base URL in api.ts matches: `http://localhost:5000`

---

## 📊 Testing Scenarios

### Scenario 1: Happy Path (Registration → Login)
```
1. Register: testuser@example.com / password123
2. Verify user appears in users.json
3. Login: testuser@example.com / password123
4. Verify token returned
5. Access protected pages
```

### Scenario 2: Validation Tests
```
1. Register with invalid email (should fail)
2. Register with short password (should fail)
3. Register duplicate email (should fail)
4. Login with wrong password (should fail)
5. Login with non-existent email (should fail)
```

### Scenario 3: Data Persistence
```
1. Stop server
2. Start server again
3. Login with previously registered user
4. Should work (data persisted in users.json)
```

---

## 🛠️ Development Commands

```bash
# Backend
npm run server              # Start server
npm run server:dev          # Start with nodemon (auto-reload)

# Frontend
npm run dev                 # Start dev server with hot reload
npm run build               # Build for production
npm run preview             # Preview production build

# Testing & Linting
npm run test                # Run tests
npm run test:watch          # Watch mode for tests
npm run lint                # Check linting
```

---

## 📚 API Documentation

See **BACKEND_SETUP.md** for detailed API documentation

### Endpoints Summary:
- `GET /` - Health check
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/users` - Get all users (testing only)

---

## 🔒 Security Notes

⚠️ **This is a development/demo setup**

For production:
- ✅ Implement hashed passwords (bcrypt)
- ✅ Use proper JWT authentication
- ✅ Add HTTPS/SSL
- ✅ Use real database (MongoDB, PostgreSQL)
- ✅ Implement rate limiting
- ✅ Add input sanitization
- ✅ Add CSRF protection
- ✅ Implement refresh tokens

---

## 📝 Data Format

### users.json Structure:
```json
[
  {
    "id": "1234567890",
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "createdAt": "2026-03-24T10:30:00.000Z"
  }
]
```

---

## 🎯 Next Steps

1. ✅ Start backend: `npm run server`
2. ✅ Start frontend: `npm run dev`
3. ✅ Test registration
4. ✅ Test login
5. ✅ Explore dashboard
6. ✅ Test other features

---

## 💡 Tips

- Keep backend running in a separate terminal
- Use VS Code REST Client for quick API testing
- Check browser console for errors
- Check terminal output for backend logs
- Look at users.json to verify data storage

---

**Status**: ✅ Backend and Frontend are fully integrated and ready to use!

For issues, check BACKEND_SETUP.md or run tests in API_TESTS.http
