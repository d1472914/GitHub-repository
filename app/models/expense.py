"""
Expense Model — 共同開支
儲存每一筆共同消費的記錄
"""

from datetime import datetime
from app.models import db


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    paid_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='expenses')
    payer = db.relationship('User', backref='paid_expenses')
    splits = db.relationship('ExpenseSplit', backref='expense', lazy='dynamic')

    def __repr__(self):
        return f'<Expense {self.title} ${self.amount}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, title, amount, paid_by, category=None):
        """建立新開支"""
        expense = cls(
            group_id=group_id,
            title=title,
            amount=amount,
            category=category,
            paid_by=paid_by
        )
        db.session.add(expense)
        db.session.commit()
        return expense

    @classmethod
    def get_all(cls):
        """取得所有開支"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, expense_id):
        """依 ID 取得開支"""
        return cls.query.get(expense_id)

    @classmethod
    def get_by_group(cls, group_id):
        """取得群組的所有開支（由新到舊）"""
        return cls.query.filter_by(group_id=group_id)\
            .order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        """更新開支"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除開支"""
        db.session.delete(self)
        db.session.commit()
