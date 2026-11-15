# Flask SQLite Tasks API

A REST API built with Python, Flask, and Flask-SQLAlchemy (ORM) that stores tasks persistently in a SQLite database.

## Endpoints
- `GET /` - Returns a welcome message.
- `GET /api/tasks` - Retrieves a JSON list of all tasks from the SQLite database.
- `POST /api/tasks` - Accepts a JSON body (e.g., `{"title": "New Task"}`) to create and persistently store a new task.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python app.py`
3. Test `GET` at `http://127.0.0` or send a `POST` request with JSON payload `{"title": "Buy groceries"}`.
