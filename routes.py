import re
import time
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, Task, LoginAttempt

USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_]{3,30}$')
api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def home():
    """Return API status message."""
    return jsonify({"message": "Authenticated Task Manager API"}), 200


@api.route('/api/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if not USERNAME_PATTERN.match(username):
        return jsonify({"error": "Username must be 3-30 alphanumeric/underscore characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "username": user.username}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while registering user"}), 500


@api.route('/api/login', methods=['POST'])
def login():
    """Authenticate user with persistent database rate-limiting."""
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    attempt = LoginAttempt.query.filter_by(username=username).first()
    if attempt and attempt.count >= 5 and (time.time() - attempt.last_attempt) < 60:
        return jsonify({"error": "Too many failed attempts. Try again in 60 seconds."}), 429

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if attempt:
            db.session.delete(attempt)
            db.session.commit()
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200

    if not attempt:
        attempt = LoginAttempt(username=username, count=1, last_attempt=time.time())
        db.session.add(attempt)
    else:
        attempt.count += 1
        attempt.last_attempt = time.time()
    db.session.commit()
    return jsonify({"error": "Invalid credentials"}), 401


@api.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Log out the current authenticated user."""
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@api.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Retrieve all tasks for the logged-in user."""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200


@api.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    """Create a validated task for the logged-in user."""
    data = request.get_json() or {}
    title = str(data.get('title', '')).strip()
    if not title or len(title) > 200:
        return jsonify({"error": "Title is required and must be 200 characters or fewer"}), 400

    try:
        task = Task(title=title, completed=bool(data.get('completed', False)), user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        return jsonify({"message": "Task added", "task": task.to_dict()}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while saving task"}), 500
