from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Task ORM model
class Task(db.Model):
    """Database model representing a task item."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convert Task object into a JSON-serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed
        }

# Create the SQLite database tables automatically
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    """Return a welcome message for the API root."""
    return jsonify({"message": "Welcome to the SQLite Tasks API! Use GET or POST on /api/tasks."})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Retrieve all tasks stored in the SQLite database."""
    tasks = Task.query.all()
    return jsonify({"tasks": [task.to_dict() for task in tasks]})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a new task from a JSON payload and save it to SQLite."""
    data = request.get_json()

    if not data or 'title' not in data or not str(data['title']).strip():
        return jsonify({"error": "Task 'title' is required"}), 400

    new_task = Task(
        title=str(data['title']).strip(),
        completed=bool(data.get('completed', False))
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task added successfully", "task": new_task.to_dict()}), 201

if __name__ == '__main__':
    app.run(debug=True)
