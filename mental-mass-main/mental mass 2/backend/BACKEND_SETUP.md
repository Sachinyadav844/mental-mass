# Backend Server Setup Guide

## Overview
MENTALMASS backend authentication server built with Node.js and Express.

## Installation

### 1. Install Dependencies
```bash
npm install express cors
```

Dependencies are already installed. You can verify with:
```bash
npm list express cors
```

### 2. Start the Backend Server

#### Option 1: Using npm script
```bash
npm run server
```

#### Option 2: Direct Node command
```bash
node server.js
```

#### Option 3: Using nodemon (auto-restart on file changes)
```bash
npm run server:dev
```
*Note: Requires nodemon installed globally or locally*

## Server Details

- **URL**: http://localhost:5000
- **Database**: users.json (mock database in project root)

## API Endpoints

### 1. Health Check
```
GET http://localhost:5000/
```
Returns: `{ message: "MENTALMASS Auth Server is running" }`

### 2. Register User
```
POST http://localhost:5000/auth/register
Content-Type: application/json

Request Body:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123"
}

Success Response (201):
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": "1234567890",
    "name": "John Doe",
    "email": "john@example.com"
  }
}

Error Responses:
- 400: Missing fields or validation errors
- 409: User already exists
- 500: Server error
```

### 3. Login User
```
POST http://localhost:5000/auth/login
Content-Type: application/json

Request Body:
{
  "email": "john@example.com",
  "password": "secure123"
}

Success Response (200):
{
  "success": true,
  "message": "Login successful",
  "token": "token-1234567890-1234567890",
  "user": {
    "id": "1234567890",
    "name": "John Doe",
    "email": "john@example.com"
  }
}

Error Responses:
- 400: Missing email or password
- 401: Invalid credentials
- 500: Server error
```

### 4. Get All Users (Testing Only)
```
GET http://localhost:5000/auth/users
```
Returns array of users without passwords

## Features

✅ **Express Server**: Fast and lightweight HTTP server
✅ **CORS Support**: Cross-origin requests enabled
✅ **JSON Middleware**: Automatic JSON parsing
✅ **File-based Database**: users.json for mock storage
✅ **Input Validation**: Email format and password strength checks
✅ **Error Handling**: Comprehensive error responses
✅ **Security Features**:
  - Email validation
  - Duplicate user prevention
  - Minimum password length requirement
  - Lowercase email normalization

## User Data Structure

```json
[
  {
    "id": "1234567890",
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123",
    "createdAt": "2026-03-24T10:30:00.000Z"
  }
]
```

## Testing with cURL or Postman

### Register:
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### Login:
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'
```

## Frontend Integration

The frontend (React) is pre-configured to communicate with this backend via:
- File: `src/services/api.ts`
- Base URL: `http://localhost:5000`
- Endpoints: `/auth/login` and `/auth/register`

**To run frontend and backend together:**

Terminal 1 (Backend):
```bash
npm run server
```

Terminal 2 (Frontend):
```bash
npm run dev
```

## Important Notes

⚠️ **Development Only**: This is a mock database using JSON files. Not suitable for production.

🔒 **Security Warnings**:
- Passwords are stored in plain text (Use bcrypt in production)
- No JWT implementation (Use proper JWT in production)
- No rate limiting
- No HTTPS

## File Structure

```
project-root/
├── server.js          # Express backend server
├── users.json         # User database (auto-created if missing)
├── package.json       # Project dependencies
└── src/               # React frontend
```

## Troubleshooting

### Port 5000 already in use
```bash
# Kill process on port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

### users.json not created
The server will automatically create `users.json` on first run if it doesn't exist.

### CORS errors
Ensure `cors()` middleware is enabled in server.js (already configured).

## Next Steps for Production

1. ✅ Add bcrypt for password hashing
2. ✅ Implement JWT authentication
3. ✅ Use database (MongoDB, PostgreSQL)
4. ✅ Add rate limiting
5. ✅ Implement HTTPS
6. ✅ Add input sanitization
7. ✅ Add logging and monitoring
8. ✅ Add email verification

---

**Status**: ✅ Backend server is ready for development and frontend integration.
