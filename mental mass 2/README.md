# MENTALMASS – AI-Based Wellness Monitoring System

## Description

MENTALMASS is an AI-powered mental wellness monitoring dashboard that enables users to track emotional health over time, visualize trends, and get real-time recommendations. It supports emotion detection, sentiment analysis, mood scoring, alerts, and journaling in a responsive web UI.

## Features

- Emotion Detection
- Text Sentiment Analysis
- Mood Score Calculation
- Wellness Alert System
- Recommendation Engine
- Self Assessment
- Dashboard Analytics
- Journal Tracking

## Tech Stack

- **Frontend**: React (Vite), TypeScript, Tailwind CSS, Axios, Recharts
- **Backend**: Python Flask, OpenCV (mock), DeepFace (mock), Transformers (mock), Scikit-learn
- **AI/ML**: Mock AI services (fallback when hardware lacks TensorFlow support)

## Installation & Running

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs on: http://localhost:8081

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Runs on http://localhost:5000
**Note**: The AI services use mock implementations when TensorFlow/DeepFace/Transformers cannot be loaded due to hardware compatibility. The system remains fully functional with realistic mock responses.
## Folder Structure

- `frontend/`: React frontend code
- `backend/`: Node.js API server
- `ai/`: AI/ML logic (currently mock)
  - `lib/`: utility helpers
  - `pages/`: route pages
  - `services/`: API services
  - `assets/`: images and static files

## Usage

1. Run the app.
2. Sign up or log in.
3. Use the navigation to access Monitor, Dashboard, Journal, and Assessment.
4. Capture live emotion, enter text for sentiment analysis, and track mood history.

## Future Scope

- PDF Report Export
- Age-based insights
- Advanced AI recommendations
- Group progress comparisons
- Secure data export/import

## Author

- Developer: [Your Name]

## Notes

- The app is branded as MENTALMASS with an AI Wellness Monitoring theme.
- All existing features and routes remain intact.
