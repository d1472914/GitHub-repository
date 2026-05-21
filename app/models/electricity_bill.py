"""
<<<<<<< HEAD
ElectricityBill Model — 電費帳單資料模型 (sqlite3 版本)
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
        print(f"Database connection error in electricity_bill model: {e}")
        raise e

def create(data):
    """
    建立新電費帳單記錄
    :param data: dict, 包含 group_id, total_amount, total_kwh, period_start, period_end, created_by
    :return: int 新增的帳單 ID 或 None
    """
    sql = """
    INSERT INTO electricity_bills (group_id, total_amount, total_kwh, period_start, period_end, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('total_amount'),
                data.get('total_kwh'),
                data.get('period_start'),
                data.get('period_end'),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create electricity_bill: {e}")
        return None

def get_all():
    """
    取得所有電費帳單記錄
    :return: list of Row
    """
    sql = "SELECT * FROM electricity_bills"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all electricity_bills: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有電費帳單，按建立時間排序由新到舊
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM electricity_bills WHERE group_id = ? ORDER BY created_at DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id bills ({group_id}): {e}")
        return []

def get_by_id(bill_id):
    """
    依 ID 取得單筆電費帳單記錄
    :param bill_id: int, 帳單 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM electricity_bills WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (bill_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id electricity_bill ({bill_id}): {e}")
        return None

def update(bill_id, data):
    """
    更新電費帳單資料
    :param bill_id: int, 帳單 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE electricity_bills SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(bill_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update electricity_bill ({bill_id}): {e}")
        return False

def delete(bill_id):
    """
    刪除電費帳單記錄
    :param bill_id: int, 帳單 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM electricity_bills WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (bill_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete electricity_bill ({bill_id}): {e}")
        return False
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
