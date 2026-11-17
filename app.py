import os, re, secrets, time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_]{3,30}$')
FAILED_LOGINS = {}  # Tracks {username: [count, last_attempt_time]} for brute-force protection

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authentication required"}), 401

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed, "user_id": self.user_id}

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Authenticated Task Manager API"}), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username, password = str(data.get('username', '')).strip(), str(data.get('password', ''))
    if not USERNAME_PATTERN.match(username):
        return jsonify({"error": "Username must be 3-30 alphanumeric/underscore characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "username": user.username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username, password = str(data.get('username', '')).strip(), str(data.get('password', ''))
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    attempts, last_time = FAILED_LOGINS.get(username, [0, 0])
    if attempts >= 5 and time.time() - last_time < 60:
        return jsonify({"error": "Too many failed attempts. Try again in 60 seconds."}), 429
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        FAILED_LOGINS.pop(username, None)
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    FAILED_LOGINS[username] = [attempts + 1, time.time()]
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]}), 200

@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json() or {}
    title = str(data.get('title', '')).strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    task = Task(title=title, completed=bool(data.get('completed', False)), user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task added", "task": task.to_dict()}), 201

if __name__ == '__main__':
    app.run(debug=True)
