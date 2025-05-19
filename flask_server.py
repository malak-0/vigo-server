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
    direction = data.get('direction')

    if not direction or not isinstance(direction, str):
        return jsonify({"error": "Invalid direction format"}), 400

    redis_client.rpush('stored_directions', direction)
    return jsonify({"message": "Direction received"}), 200

# Get and remove the next direction (like a queue)
@server.route('/pop_direction', methods=['GET'])
def pop_direction():
    direction = redis_client.lpop('stored_directions')
    if direction:
        return jsonify({"direction": direction.decode('utf-8')}), 200
    else:
        return jsonify({"message": "No directions yet"}), 204

# Start the Flask server
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
