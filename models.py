from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    fcm_token = db.Column(db.String(255), nullable=False)

    def __init__(self, device_id, fcm_token):
        self.device_id = device_id
        self.fcm_token = fcm_token
