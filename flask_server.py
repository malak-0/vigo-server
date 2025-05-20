from flask import Flask, request, jsonify
from models import db, Device
import os
import redis
import json

# Initialize Flask app
server = Flask(__name__)

# Load secret API key from environment variable
SECRET_API_KEY = os.environ.get("SECRET_API_KEY")

# access the db on railway
server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(server)

# Connect to Redis using the environment variable
redis_url = os.environ.get("REDIS_URL")
redis_client = redis.from_url(redis_url)

# Check Redis connection
try:
    redis_client.ping()
except redis.exceptions.ConnectionError as e:
    print(f"Redis connection failed: {e}")


# Initialize the database tables
with server.app_context():
    db.create_all()

# Register device token
@server.route('/register-token', methods=['POST'])
def register_token():
    api_key = request.headers.get('x-api-key')
    if api_key != SECRET_API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    token = data.get('token')
    device_id = data.get('device_id')

    if not token:
        return jsonify({'error': 'Token missing'}), 400
    if not device_id:
        return jsonify({'error': 'Device ID missing'}), 400

    # Always keep just the first device record
    device = Device.query.first()
    if device:
        device.device_id = device_id
        device.fcm_token = token
    else:
        device = Device(device_id=device_id, fcm_token=token)
        db.session.add(device)

    db.session.commit()
    print(f"Stored token for device {device_id}")
    return jsonify({'message': 'Token saved'}), 200

# Get the single stored token
@server.route('/get-single-token', methods=['GET'])
def get_single_token():
    device = Device.query.first()
    if device:
        return jsonify({'device_id': device.device_id, 'fcm_token': device.fcm_token})
    else:
        return jsonify({'error': 'No device found'}), 404

stored_directions = []

# Receive directions from the app
@server.route('/receive_directions', methods=['POST'])
def receive_directions():
    data = request.get_json()
    directions = data.get('directions', [])

    if not directions:
        return jsonify({"error": "No directions received"}), 400
    
    # Store new directions, overwriting the previous value
    redis_client.set('stored_directions', json.dumps(directions))

    return jsonify({"message": "Directions received successfully", "count": len(directions)}), 200

# endpoint to access directions outside 
@server.route('/get_directions', methods=['GET'])
def get_directions():
    raw = redis_client.get('stored_directions')
    if raw is None:
        return jsonify({"error": "No directions found"}), 404
    directions = json.loads(raw)
    return jsonify({"directions": directions})
    
# @server.route('/todo', methods=['POST'])
# def create_task():
#     data = request.get_json()
#     desc = data.get('description')
#     time = data.get('time')  # Format: "HH:MM" or None

#     if not desc:
#         return jsonify({"error": "Task description is required"}), 400

#     task = Task(description=desc)
#     if time:
#         from datetime import datetime
#         try:
#             task.time = datetime.strptime(time, "%H:%M").time()
#         except ValueError:
#             return jsonify({"error": "Invalid time format"}), 400

#     db.session.add(task)
#     db.session.commit()
#     return jsonify({"message": "Task created", "task": task.to_dict()}), 201

# @server.route('/todo', methods=['GET'])
# def get_all_tasks():
#     tasks = Task.query.order_by(Task.created_at.desc()).all()
#     return jsonify([task.to_dict() for task in tasks])

# @server.route('/todo/<int:task_id>/done', methods=['PATCH'])
# def mark_task_done(task_id):
#     task = Task.query.get(task_id)
#     if not task:
#         return jsonify({"error": "Task not found"}), 404
#     task.is_done = True
#     db.session.commit()
#     return jsonify({"message": "Task marked as done", "task": task.to_dict()})

# @server.route('/todo/pending', methods=['GET'])
# def get_pending_tasks():
#     tasks = Task.query.filter_by(is_done=False).order_by(Task.created_at.asc()).all()
#     return jsonify([task.to_dict() for task in tasks])


# Start the Flask server
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
