from datetime import datetime
from app import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    meter_records = db.relationship('MeterRecord', backref='room', lazy=True)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    total_degrees = db.Column(db.Float, nullable=False)
    public_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    meter_records = db.relationship('MeterRecord', backref='bill', lazy=True, cascade="all, delete-orphan")

class MeterRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_degree = db.Column(db.Float, nullable=False)
    end_degree = db.Column(db.Float, nullable=False)
    personal_amount = db.Column(db.Float, nullable=False)
    public_shared_amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    
    @property
    def total_due(self):
        return self.personal_amount + self.public_shared_amount
    
    @property
    def used_degrees(self):
        return self.end_degree - self.start_degree
