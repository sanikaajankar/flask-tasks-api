# Authenticated Flask Task Manager API

A secure REST API built with Python, Flask, Flask-Login, and SQLite (Flask-SQLAlchemy) featuring user registration, password hashing, brute-force login protection, and user-specific task management.

## Endpoints
- `GET /` - Returns API status message.
- `POST /api/register` - Register a new user with JSON `{"username": "alice", "password": "secretpassword"}`.
- `POST /api/login` - Authenticate and start a session with JSON `{"username": "alice", "password": "secretpassword"}`.
- `POST /api/logout` - End the current session (requires login).
- `GET /api/tasks` - Retrieve all tasks for the logged-in user (requires login).
- `POST /api/tasks` - Create a new task with JSON `{"title": "Complete project"}` (requires login).

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python app.py`
3. Open `http://localhost:5000/` in your browser or API client.
