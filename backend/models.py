from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'patient' or 'caregiver'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    medications = db.relationship('Medication', backref='patient', lazy=True, cascade="all, delete-orphan")
    sos_alerts = db.relationship('SOSAlert', backref='patient', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    blood_type = db.Column(db.String(10), nullable=True)
    
    # New fields for frontend
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.String(20), nullable=True)
    weight = db.Column(db.String(20), nullable=True)
    conditions = db.Column(db.String(255), nullable=True)
    allergies = db.Column(db.String(255), nullable=True)
    
    # Emergency Contact specific fields
    ec_name = db.Column(db.String(100), nullable=True)
    ec_rel = db.Column(db.String(50), nullable=True)
    ec_phone = db.Column(db.String(20), nullable=True)

    primary_doctors = db.Column(db.JSON, nullable=True) # List of {"name": "...", "clinic": "..."}
    language = db.Column(db.String(10), default='en') # 'en', 'kn', 'hi'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "blood_type": self.blood_type,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "conditions": self.conditions,
            "allergies": self.allergies,
            "ec_name": self.ec_name,
            "ec_rel": self.ec_rel,
            "ec_phone": self.ec_phone,
            "primary_doctors": self.primary_doctors or [],
            "language": self.language,
            "updated_at": self.updated_at.isoformat()
        }

class CaregiverRelation(db.Model):
    __tablename__ = 'caregiver_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active') # 'active', 'pending'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Adding explicit relationship anchors
    patient_user = db.relationship('User', foreign_keys=[patient_id], backref='caregiver_links')
    caregiver_user = db.relationship('User', foreign_keys=[caregiver_id], backref='patient_links')

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "caregiver_id": self.caregiver_id,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active') # 'active', 'resolved'
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "triggered_at": self.triggered_at.isoformat()
        }

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False) # e.g. "500mg"
    frequency = db.Column(db.String(50), nullable=False) # e.g. "Daily"
    time_of_day = db.Column(db.String(50), nullable=False) # e.g. "08:00 AM"
    is_taken = db.Column(db.Boolean, default=False)
    last_taken_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "time_of_day": self.time_of_day,
            "is_taken": self.is_taken,
            "last_taken_at": self.last_taken_at.isoformat() if self.last_taken_at else None
        }

class VitalsLog(db.Model):
    __tablename__ = 'vitals_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False) # 'heart_rate', 'bp_systolic', 'bp_diastolic', 'sleep_hours', 'steps'
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "timestamp": self.timestamp.isoformat()
        }

class CaregiverInvitation(db.Model):
    __tablename__ = 'caregiver_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender_user = db.relationship('User', foreign_keys=[sender_id], backref='sent_invitations')

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_email": self.receiver_email,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat()
        }

