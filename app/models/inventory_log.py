"""
<<<<<<< HEAD
InventoryLog Model — 物資操作記錄 (sqlite3 版本)
記錄每次入庫或出庫的操作
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線並啟用外鍵"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error in inventory_log model: {e}")
        raise e

def create(data):
    """
    建立新操作記錄
    :param data: dict, 包含 item_id, user_id, action, quantity, note
    :return: int 新增的記錄 ID 或 None
    """
    sql = """
    INSERT INTO inventory_logs (item_id, user_id, action, quantity, note)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('item_id'),
                data.get('user_id'),
                data.get('action'),
                data.get('quantity'),
                data.get('note')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create inventory_log: {e}")
        return None

def get_all():
    """
    取得所有操作記錄
    :return: list of Row 物件
    """
    sql = "SELECT * FROM inventory_logs ORDER BY id DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all inventory_logs: {e}")
        return []

def get_by_id(log_id):
    """
    依 ID 取得操作記錄
    :param log_id: int, 記錄 ID
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM inventory_logs WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (log_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id inventory_log ({log_id}): {e}")
        return None

def get_by_item(item_id):
    """
    取得某物資的所有操作記錄（由新到舊）
    :param item_id: int, 物資 ID
    :return: list of Row 物件
    """
    sql = "SELECT * FROM inventory_logs WHERE item_id = ? ORDER BY id DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (item_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_item inventory_logs ({item_id}): {e}")
        return []

def update(log_id, data):
    """
    更新操作記錄
    :param log_id: int, 記錄 ID
    :param data: dict, 需要更新的欄位值，例如 {'note': '新備註', 'quantity': 10}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE inventory_logs SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(log_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update inventory_log ({log_id}): {e}")
        return False

def delete(log_id):
    """
    刪除操作記錄
    :param log_id: int, 記錄 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM inventory_logs WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (log_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete inventory_log ({log_id}): {e}")
        return False
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
