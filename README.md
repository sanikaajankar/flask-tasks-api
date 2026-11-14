# Flask Tasks API

A REST API built with Python and Flask that retrieves tasks and allows adding new tasks via JSON POST requests.

## Endpoints
- `GET /` - Returns a welcome message.
- `GET /api/tasks` - Returns a JSON list of all tasks.
- `POST /api/tasks` - Accepts a JSON body (e.g., `{"title": "New Task"}`) to create and return a new task.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python app.py`
3. Test `GET` at `http://127.0.0` or send a `POST` request with JSON payload `{"title": "Buy groceries"}`.
