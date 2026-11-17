from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Registered user account model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def set_password(self, password):
        """Hash and store password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify plaintext password against stored hash."""
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    """Task item model linked to an authenticated user."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        """Serialize task to dictionary."""
        return {"id": self.id, "title": self.title, "completed": self.completed, "user_id": self.user_id}


class LoginAttempt(db.Model):
    """Persistent tracking of failed login attempts for rate limiting."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.Float, default=0.0)
