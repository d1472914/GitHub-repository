"""
<<<<<<< HEAD
ElectricitySplit Model — 電費分攤結果資料模型 (sqlite3 版本)
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
        print(f"Database connection error in electricity_split model: {e}")
        raise e

def create(data):
    """
    建立新電費分攤記錄
    :param data: dict, 包含 bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid
    :return: int 新增的分攤記錄 ID 或 None
    """
    sql = """
    INSERT INTO electricity_splits (bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('bill_id'),
                data.get('user_id'),
                data.get('personal_amount'),
                data.get('shared_amount'),
                data.get('total_amount'),
                data.get('is_paid', 0)
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create electricity_split: {e}")
        return None

def get_all():
    """
    取得所有電費分攤結果記錄
    :return: list of Row
    """
    sql = "SELECT * FROM electricity_splits"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all electricity_splits: {e}")
        return []

def get_by_bill_id(bill_id):
    """
    取得某一期電費帳單的所有分攤結果
    :param bill_id: int, 帳單 ID
    :return: list of Row
    """
    sql = "SELECT * FROM electricity_splits WHERE bill_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (bill_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_bill_id splits ({bill_id}): {e}")
        return []

def get_by_id(split_id):
    """
    依 ID 取得單筆電費分攤記錄
    :param split_id: int, 分攤結果 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM electricity_splits WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (split_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id electricity_split ({split_id}): {e}")
        return None

def update(split_id, data):
    """
    更新電費分攤狀態（如標記為已付清）
    :param split_id: int, 分攤結果 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE electricity_splits SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(split_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update electricity_split ({split_id}): {e}")
        return False

def delete(split_id):
    """
    刪除電費分攤記錄
    :param split_id: int, 分攤結果 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM electricity_splits WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (split_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete electricity_split ({split_id}): {e}")
        return False
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
