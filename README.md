# Authenticated Flask Task Manager API

A secure REST API built with Python, Flask, Flask-Login, and SQLite (Flask-SQLAlchemy) featuring user registration, password hashing, session authentication, and user-specific task management.

## Endpoints
- `GET /` - Returns API overview and available routes.
- `POST /api/register` - Register a new account with JSON `{"username": "alice", "password": "secretpassword"}`.
- `POST /api/login` - Log in with JSON `{"username": "alice", "password": "secretpassword"}`.
- `POST /api/logout` - Log out of the current session (requires login).
- `GET /api/tasks` - Retrieve all tasks for the logged-in user (requires login).
- `POST /api/tasks` - Create a new task for the logged-in user with JSON `{"title": "Complete project"}` (requires login).

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Access the API at `http://127.0.0`
