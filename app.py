from flask import Flask, jsonify

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Learn Flask basics", "completed": True},
    {"id": 2, "title": "Build a REST API endpoint", "completed": False},
    {"id": 3, "title": "Push project to GitHub", "completed": False}
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Tasks API! Visit /api/tasks to see the task list."})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)
