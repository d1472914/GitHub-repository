"""
Group Model — 群組資料模型 (sqlite3 版本)
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
        print(f"Database connection error in group model: {e}")
        raise e

def create(data):
    """
    建立新群組記錄
    :param data: dict, 包含 name, invite_code, created_by
    :return: int 新增的群組 ID 或 None
    """
    sql = """
    INSERT INTO groups (name, invite_code, created_by)
    VALUES (?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('name'),
                data.get('invite_code'),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create group: {e}")
        return None

def get_all():
    """
    取得所有群組記錄
    :return: list of Row
    """
    sql = "SELECT * FROM groups"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all groups: {e}")
        return []

def get_by_id(group_id):
    """
    依 ID 取得單筆群組記錄
    :param group_id: int, 群組 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM groups WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id group ({group_id}): {e}")
        return None

def get_by_invite_code(invite_code):
    """
    依邀請碼取得單筆群組記錄
    :param invite_code: str, 邀請碼
    :return: Row 或 None
    """
    sql = "SELECT * FROM groups WHERE invite_code = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (invite_code,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_invite_code group ({invite_code}): {e}")
        return None

def update(group_id, data):
    """
    更新群組資料
    :param group_id: int, 群組 ID
    :param data: dict, 需要更新的欄位值，例如 {'name': '新群組名稱'}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE groups SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(group_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting group: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        print(f"Error in update group ({group_id}): {e}")
        return False

def delete(group_id):
    """
    刪除群組記錄
    :param group_id: int, 群組 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM groups WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (group_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete group ({group_id}): {e}")
        return False
