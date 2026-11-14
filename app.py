from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Learn Flask basics", "completed": True},
    {"id": 2, "title": "Build a REST API endpoint", "completed": False},
    {"id": 3, "title": "Push project to GitHub", "completed": False}
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Tasks API! Use GET or POST on /api/tasks."})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"tasks": tasks})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    
    if not data or 'title' not in data or not str(data['title']).strip():
        return jsonify({"error": "Task 'title' is required"}), 400

    new_task = {
        "id": len(tasks) + 1,
        "title": data['title'].strip(),
        "completed": bool(data.get('completed', False))
    }
    tasks.append(new_task)
    
    return jsonify({"message": "Task added successfully", "task": new_task}), 201

if __name__ == '__main__':
    app.run(debug=True)
