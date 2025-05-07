from flask import Flask, request, jsonify
from models import db, Device
import os

server = Flask(__name__)
SECRET_API_KEY = os.environ.get("SECRET_API_KEY")
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fcm_tokens.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(server)

# create the db if not exist
@server.before_first_request
def create_tables():
    db.create_all()

# endpoint to register the token from the app
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

    device = Device.query.filter_by(device_id=device_id).first()
    if device:
        device.fcm_token = token
    else:
        device = Device(device_id=device_id, fcm_token=token)
        db.session.add(device)

    db.session.commit()
    print(f"Stored token for device {device_id}")
    return jsonify({'message': 'Token saved'}), 200

# endpoint to get the token to use it outside
@server.route('/get-single-token', methods=['GET'])
def get_single_token():
    device = Device.query.first()  # Only one row expected
    if device:
        return jsonify({'device_id': device.device_id, 'fcm_token': device.fcm_token})
    else:
        return jsonify({'error': 'No device found'}), 404
    
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

