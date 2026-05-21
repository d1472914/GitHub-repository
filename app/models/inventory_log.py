"""
InventoryLog Model — 物資操作記錄
記錄每次入庫或出庫的操作
"""

from datetime import datetime
from app.models import db


class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # stock_in / stock_out
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    user = db.relationship('User', backref='inventory_logs')

    def __repr__(self):
        return f'<InventoryLog {self.action} item={self.item_id} qty={self.quantity}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, item_id, user_id, action, quantity, note=None):
        """建立操作記錄"""
        log = cls(
            item_id=item_id,
            user_id=user_id,
            action=action,
            quantity=quantity,
            note=note
        )
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_all(cls):
        """取得所有操作記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, log_id):
        """依 ID 取得操作記錄"""
        return cls.query.get(log_id)

    @classmethod
    def get_by_item(cls, item_id):
        """取得某物資的所有操作記錄（由新到舊）"""
        return cls.query.filter_by(item_id=item_id)\
            .order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        """更新操作記錄"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除操作記錄"""
        db.session.delete(self)
        db.session.commit()
