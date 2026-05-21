"""
ElectricitySplit Model — 電費分攤
儲存每期電費帳單的分攤結果
"""

from app.models import db


class ElectricitySplit(db.Model):
    __tablename__ = 'electricity_splits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('electricity_bills.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    personal_amount = db.Column(db.Float, nullable=False)
    shared_amount = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, nullable=False, default=False)

    # 關聯
    user = db.relationship('User', backref='electricity_splits')

    def __repr__(self):
        return f'<ElectricitySplit bill={self.bill_id} user={self.user_id} ${self.total_amount}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, bill_id, user_id, personal_amount, shared_amount, total_amount):
        """建立電費分攤記錄"""
        split = cls(
            bill_id=bill_id,
            user_id=user_id,
            personal_amount=personal_amount,
            shared_amount=shared_amount,
            total_amount=total_amount
        )
        db.session.add(split)
        db.session.commit()
        return split

    @classmethod
    def get_all(cls):
        """取得所有電費分攤"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, split_id):
        """依 ID 取得電費分攤"""
        return cls.query.get(split_id)

    @classmethod
    def get_by_bill(cls, bill_id):
        """取得某期帳單的所有分攤"""
        return cls.query.filter_by(bill_id=bill_id).all()

    def update(self, **kwargs):
        """更新電費分攤"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除電費分攤"""
        db.session.delete(self)
        db.session.commit()
