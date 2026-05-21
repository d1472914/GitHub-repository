"""
InventoryItem Model — 物資品項
儲存共同物資的品項與庫存狀態
"""

from datetime import datetime
from app.models import db


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    min_quantity = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='inventory_items')
    creator = db.relationship('User', backref='created_inventory_items')
    logs = db.relationship('InventoryLog', backref='item', lazy='dynamic',
                           order_by='InventoryLog.created_at.desc()')

    def __repr__(self):
        return f'<InventoryItem {self.name} qty={self.quantity}>'

    @property
    def is_low_stock(self):
        """是否低於最低庫存"""
        return self.quantity <= self.min_quantity

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, name, unit, created_by, quantity=0, min_quantity=0):
        """建立新物資品項"""
        item = cls(
            group_id=group_id,
            name=name,
            unit=unit,
            quantity=quantity,
            min_quantity=min_quantity,
            created_by=created_by
        )
        db.session.add(item)
        db.session.commit()
        return item

    @classmethod
    def get_all(cls):
        """取得所有物資品項"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, item_id):
        """依 ID 取得物資品項"""
        return cls.query.get(item_id)

    @classmethod
    def get_by_group(cls, group_id):
        """取得群組的所有物資品項"""
        return cls.query.filter_by(group_id=group_id)\
            .order_by(cls.name.asc()).all()

    @classmethod
    def get_low_stock_by_group(cls, group_id):
        """取得群組中低庫存的物資品項"""
        return cls.query.filter(
            cls.group_id == group_id,
            cls.quantity <= cls.min_quantity
        ).all()

    def stock_in(self, qty):
        """入庫：增加庫存"""
        self.quantity += qty
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def stock_out(self, qty):
        """出庫：減少庫存"""
        self.quantity = max(0, self.quantity - qty)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update(self, **kwargs):
        """更新物資品項"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def delete(self):
        """刪除物資品項"""
        db.session.delete(self)
        db.session.commit()
