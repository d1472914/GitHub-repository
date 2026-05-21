"""
ExpenseSplit Model — 開支分攤
記錄每筆開支中，每人應分攤的金額與結清狀態
"""

from app.models import db


class ExpenseSplit(db.Model):
    __tablename__ = 'expense_splits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_settled = db.Column(db.Boolean, nullable=False, default=False)

    # 關聯
    user = db.relationship('User', backref='expense_splits')

    def __repr__(self):
        return f'<ExpenseSplit expense={self.expense_id} user={self.user_id} ${self.amount}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, expense_id, user_id, amount):
        """建立分攤記錄"""
        split = cls(
            expense_id=expense_id,
            user_id=user_id,
            amount=amount
        )
        db.session.add(split)
        db.session.commit()
        return split

    @classmethod
    def get_all(cls):
        """取得所有分攤記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, split_id):
        """依 ID 取得分攤記錄"""
        return cls.query.get(split_id)

    @classmethod
    def get_by_expense(cls, expense_id):
        """取得某筆開支的所有分攤"""
        return cls.query.filter_by(expense_id=expense_id).all()

    @classmethod
    def get_unsettled_by_user(cls, user_id):
        """取得某使用者所有未結清的分攤"""
        return cls.query.filter_by(user_id=user_id, is_settled=False).all()

    def update(self, **kwargs):
        """更新分攤記錄"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除分攤記錄"""
        db.session.delete(self)
        db.session.commit()
