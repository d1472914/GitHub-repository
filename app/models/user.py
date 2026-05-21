"""
User Model — 使用者資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """
    建立 SQLite 資料庫連線，並設定 row_factory 為 Row。
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error in user model: {e}")
        raise e

def create(data):
    """
    建立新使用者記錄
    :param data: dict, 包含 email, password_hash, nickname, role, group_id
    :return: int 新增的使用者 ID 或 None
    """
    sql = """
    INSERT INTO users (email, password_hash, nickname, role, group_id)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('email'),
                data.get('password_hash'),
                data.get('nickname'),
                data.get('role', 'member'),
                data.get('group_id')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create user: {e}")
        return None

def get_all():
    """
    取得所有使用者記錄
    :return: list of Row 物件
    """
    sql = "SELECT * FROM users"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all users: {e}")
        return []

def get_by_id(user_id):
    """
    依 ID 取得單筆使用者記錄
    :param user_id: int, 使用者 ID
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM users WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id user ({user_id}): {e}")
        return None

def get_by_email(email):
    """
    依 Email 取得單筆使用者記錄 (供認證路由使用)
    :param email: str, 使用者信箱
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM users WHERE email = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (email,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_email user ({email}): {e}")
        return None

def get_by_group_id(group_id):
    """
    依群組 ID 取得該群組內的所有使用者
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM users WHERE group_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id users ({group_id}): {e}")
        return []

def update(user_id, data):
    """
    更新使用者資料
    :param user_id: int, 使用者 ID
    :param data: dict, 需要更新的欄位值，例如 {'nickname': '新暱稱', 'group_id': 2}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE users SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(user_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update user ({user_id}): {e}")
        return False

def delete(user_id):
    """
    刪除使用者記錄
    :param user_id: int, 使用者 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM users WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete user ({user_id}): {e}")
        return False
