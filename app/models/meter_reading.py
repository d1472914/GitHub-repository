"""
MeterReading Model — 電表度數
記錄每期帳單中，各室友的電表起始與結束度數
"""

from app.models import db


class MeterReading(db.Model):
    __tablename__ = 'meter_readings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('electricity_bills.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_reading = db.Column(db.Float, nullable=False)
    end_reading = db.Column(db.Float, nullable=False)
    personal_kwh = db.Column(db.Float, nullable=False)

    # 唯一約束：每人每期只能登錄一次
    __table_args__ = (
        db.UniqueConstraint('bill_id', 'user_id', name='uq_bill_user_reading'),
    )

    # 關聯
    user = db.relationship('User', backref='meter_readings')

    def __repr__(self):
        return f'<MeterReading bill={self.bill_id} user={self.user_id} {self.personal_kwh}kWh>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, bill_id, user_id, start_reading, end_reading):
        """建立電表度數記錄（自動計算 personal_kwh）"""
        reading = cls(
            bill_id=bill_id,
            user_id=user_id,
            start_reading=start_reading,
            end_reading=end_reading,
            personal_kwh=end_reading - start_reading
        )
        db.session.add(reading)
        db.session.commit()
        return reading

    @classmethod
    def get_all(cls):
        """取得所有電表度數"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, reading_id):
        """依 ID 取得電表度數"""
        return cls.query.get(reading_id)

    @classmethod
    def get_by_bill(cls, bill_id):
        """取得某期帳單的所有電表度數"""
        return cls.query.filter_by(bill_id=bill_id).all()

    def update(self, **kwargs):
        """更新電表度數"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        # 重新計算個人用電
        if 'start_reading' in kwargs or 'end_reading' in kwargs:
            self.personal_kwh = self.end_reading - self.start_reading
        db.session.commit()
        return self

    def delete(self):
        """刪除電表度數"""
        db.session.delete(self)
        db.session.commit()
