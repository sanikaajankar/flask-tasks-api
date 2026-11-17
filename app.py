import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Security & SQLite Database Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.unauthorized_handler
def unauthorized():
    """Return a JSON 401 response when an unauthenticated user accesses a protected route."""
    return jsonify({"error": "Authentication required. Please log in."}), 401


class User(UserMixin, db.Model):
    """Database model representing a registered user."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def set_password(self, password):
        """Hash and store the user's password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    """Database model representing a task item belonging to a user."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        """Convert Task object into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "user_id": self.user_id
        }


@login_manager.user_loader
def load_user(user_id):
    """Load a user by ID for Flask-Login session management."""
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def home():
    """Return a welcome message and available API endpoints."""
    return jsonify({
        "message": "Welcome to the Authenticated Task Manager API!",
        "endpoints": {
            "register": "POST /api/register",
            "login": "POST /api/login",
            "logout": "POST /api/logout",
            "tasks": "GET, POST /api/tasks (Login required)"
        }
    })


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user with a hashed password."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    username = str(data['username']).strip()
    password = str(data['password'])

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "username": new_user.username}), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate an existing user and start a session."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=str(data['username']).strip()).first()
    if not user or not user.check_password(str(data['password'])):
        return jsonify({"error": "Invalid username or password"}), 401

    login_user(user)
    return jsonify({"message": f"Logged in as {user.username}"}), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Log out the currently authenticated user."""
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Retrieve all tasks belonging to the currently logged-in user."""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({"tasks": [task.to_dict() for task in tasks]})


@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    """Create a new task for the currently logged-in user."""
    data = request.get_json()
    if not data or 'title' not in data or not str(data['title']).strip():
        return jsonify({"error": "Task 'title' is required"}), 400

    new_task = Task(
        title=str(data['title']).strip(),
        completed=bool(data.get('completed', False)),
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task added successfully", "task": new_task.to_dict()}), 201


if __name__ == '__main__':
    app.run(debug=True)
