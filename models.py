from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    fcm_token = db.Column(db.String(255), nullable=False)

    def __init__(self, device_id, fcm_token):
        self.device_id = device_id
        self.fcm_token = fcm_token

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    time = db.Column(db.Time, nullable=True)  # Optional time-based reminder
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "time": self.time.strftime("%H:%M") if self.time else None,
            "is_done": self.is_done,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }