# React FastAPI Authentication App

This is a full-stack application with a React frontend and FastAPI backend, featuring user authentication and SQLite database storage.

## Project Structure

```
.
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── contexts/
    │   ├── services/
    │   └── App.tsx
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

The backend server will run on http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required packages:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend application will run on http://localhost:3000

## Features

- User registration and login
- JWT-based authentication
- Protected routes
- SQLite database storage
- Material-UI components for a modern look

## API Endpoints

- POST /register - Register a new user
- POST /token - Login and get access token
- GET /users/me - Get current user information

## Security Notes

- The SECRET_KEY in auth.py should be changed in production
- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is configured to allow requests from the frontend 