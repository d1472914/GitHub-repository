"""
Expense Model — 共同開支資料模型 (sqlite3 版本)
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
        print(f"Database connection error in expense model: {e}")
        raise e

def create(data):
    """
    建立新開支記錄
    :param data: dict, 包含 group_id, title, amount, category, paid_by
    :return: int 新增的開支 ID 或 None
    """
    sql = """
    INSERT INTO expenses (group_id, title, amount, category, paid_by)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('title'),
                data.get('amount'),
                data.get('category'),
                data.get('paid_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create expense: {e}")
        return None

def get_all():
    """
    取得所有開支記錄
    :return: list of Row
    """
    sql = "SELECT * FROM expenses"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all expenses: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有開支記錄，並按時間由新到舊排序
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM expenses WHERE group_id = ? ORDER BY created_at DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id expenses ({group_id}): {e}")
        return []

def get_by_id(expense_id):
    """
    依 ID 取得單筆開支記錄
    :param expense_id: int, 開支 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM expenses WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (expense_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id expense ({expense_id}): {e}")
        return None

def update(expense_id, data):
    """
    更新開支資料
    :param expense_id: int, 開支 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE expenses SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(expense_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update expense ({expense_id}): {e}")
        return False

def delete(expense_id):
    """
    刪除開支記錄
    :param expense_id: int, 開支 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM expenses WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (expense_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete expense ({expense_id}): {e}")
        return False
