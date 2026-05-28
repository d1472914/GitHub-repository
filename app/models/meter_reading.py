"""
MeterReading Model — 電表度數資料模型 (sqlite3 版本)
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
        print(f"Database connection error in meter_reading model: {e}")
        raise e

def create(data):
    """
    建立新電表度數記錄
    :param data: dict, 包含 bill_id, user_id, start_reading, end_reading, personal_kwh
    :return: int 新增的度數記錄 ID 或 None
    """
    sql = """
    INSERT INTO meter_readings (bill_id, user_id, start_reading, end_reading, personal_kwh)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('bill_id'),
                data.get('user_id'),
                data.get('start_reading'),
                data.get('end_reading'),
                data.get('personal_kwh')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create meter_reading: {e}")
        return None

def get_all():
    """
    取得所有度數記錄
    :return: list of Row
    """
    sql = "SELECT * FROM meter_readings"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all meter_readings: {e}")
        return []

def get_by_bill_id(bill_id):
    """
    取得某一期電費帳單的所有電表度數登錄記錄
    :param bill_id: int, 帳單 ID
    :return: list of Row
    """
    sql = "SELECT * FROM meter_readings WHERE bill_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (bill_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_bill_id readings ({bill_id}): {e}")
        return []

def get_by_id(reading_id):
    """
    依 ID 取得單筆電表度數記錄
    :param reading_id: int, 度數記錄 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM meter_readings WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (reading_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id meter_reading ({reading_id}): {e}")
        return None

def get_by_bill_and_user(bill_id, user_id):
    """
    依帳單與使用者 ID 取得特定的度數記錄
    :param bill_id: int, 帳單 ID
    :param user_id: int, 使用者 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM meter_readings WHERE bill_id = ? AND user_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (bill_id, user_id)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_bill_and_user: {e}")
        return None

def update(reading_id, data):
    """
    更新電表度數資料
    :param reading_id: int, 度數記錄 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE meter_readings SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(reading_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update meter_reading ({reading_id}): {e}")
        return False

def delete(reading_id):
    """
    刪除電表度數記錄
    :param reading_id: int, 度數記錄 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM meter_readings WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (reading_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete meter_reading ({reading_id}): {e}")
        return False
