from flask import Flask, request, jsonify
from models import db, Device
import os

# Initialize Flask app
server = Flask(__name__)

# Load secret API key from environment variable
SECRET_API_KEY = os.environ.get("SECRET_API_KEY")

# Set full absolute path for the SQLite DB
DB_PATH = 'C:/Users/malakmaloook/Smart glasses/flask server/fcm_tokens.db'
server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(server)

# Ensure the database and tables are created at startup
with server.app_context():
    print(f"Database will be created at: {DB_PATH}")
    db.create_all()

# === ROUTES ===

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

# Receive directions from the app
@server.route('/receive_directions', methods=['POST'])
def receive_directions():
    data = request.get_json()
    directions = data.get('directions', [])

    if not directions:
        return jsonify({"error": "No directions received"}), 400

    print("Received directions:")
    for idx, instruction in enumerate(directions, start=1):
        print(f"{idx}. {instruction}")

    return jsonify({"message": "Directions received successfully", "count": len(directions)}), 200

# Start the Flask server
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

