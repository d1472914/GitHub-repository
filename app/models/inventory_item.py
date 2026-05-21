"""
<<<<<<< HEAD
InventoryItem Model — 物資品項資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error in inventory_item model: {e}")
        raise e

def create(data):
    """
    建立新物資品項記錄
    :param data: dict, 包含 group_id, name, unit, quantity, min_quantity, created_by
    :return: int 新增的品項 ID 或 None
    """
    sql = """
    INSERT INTO inventory_items (group_id, name, unit, quantity, min_quantity, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('name'),
                data.get('unit'),
                data.get('quantity', 0),
                data.get('min_quantity', 0),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create inventory_item: {e}")
        return None

def get_all():
    """
    取得所有物資品項
    :return: list of Row
    """
    sql = "SELECT * FROM inventory_items"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all inventory_items: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有物資品項列表，並按品項名稱排序
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM inventory_items WHERE group_id = ? ORDER BY name ASC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id inventory_items ({group_id}): {e}")
        return []

def get_by_id(item_id):
    """
    依 ID 取得單筆物資品項
    :param item_id: int, 物資 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM inventory_items WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (item_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id inventory_item ({item_id}): {e}")
        return None

def update(item_id, data):
    """
    更新物資資訊
    :param item_id: int, 物資 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    if 'updated_at' not in keys:
        keys.append('updated_at')
        data['updated_at'] = 'CURRENT_TIMESTAMP'
        
    set_clauses = []
    params = []
    for key in keys:
        if key == 'updated_at' and data[key] == 'CURRENT_TIMESTAMP':
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        else:
            set_clauses.append(f"{key} = ?")
            params.append(data[key])
            
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE inventory_items SET {set_clause} WHERE id = ?"
    params.append(item_id)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update inventory_item ({item_id}): {e}")
        return False

def adjust_stock(item_id, qty_diff):
    """
    調整庫存量 (入庫為正，出庫為負)，並自動更新更新時間 (updated_at)
    :param item_id: int, 物資 ID
    :param qty_diff: int, 庫存增減量
    :return: bool 是否成功
    """
    sql = """
    UPDATE inventory_items
    SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (qty_diff, item_id))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in adjust_stock ({item_id}): {e}")
        return False

def delete(item_id):
    """
    刪除物資品項
    :param item_id: int, 物資 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM inventory_items WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete inventory_item ({item_id}): {e}")
        return False
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
