"""
ElectricityBill Model — 電費帳單
儲存每期電費帳單的總金額與計費期間
"""

from datetime import datetime
from app.models import db


class ElectricityBill(db.Model):
    __tablename__ = 'electricity_bills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    total_kwh = db.Column(db.Float, nullable=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='electricity_bills')
    creator = db.relationship('User', backref='created_bills')
    readings = db.relationship('MeterReading', backref='bill', lazy='dynamic')
    splits = db.relationship('ElectricitySplit', backref='bill', lazy='dynamic')

    def __repr__(self):
        return f'<ElectricityBill {self.period_start} ~ {self.period_end}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, total_amount, period_start, period_end, created_by, total_kwh=None):
        """建立新帳單"""
        bill = cls(
            group_id=group_id,
            total_amount=total_amount,
            total_kwh=total_kwh,
            period_start=period_start,
            period_end=period_end,
            created_by=created_by
        )
        db.session.add(bill)
        db.session.commit()
        return bill

    @classmethod
    def get_all(cls):
        """取得所有帳單"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, bill_id):
        """依 ID 取得帳單"""
        return cls.query.get(bill_id)

    @classmethod
    def get_by_group(cls, group_id):
        """取得群組的所有帳單（由新到舊）"""
        return cls.query.filter_by(group_id=group_id)\
            .order_by(cls.period_end.desc()).all()

    def update(self, **kwargs):
        """更新帳單"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除帳單"""
        db.session.delete(self)
        db.session.commit()
