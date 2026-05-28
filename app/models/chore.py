"""
Chore Model — 家事任務資料模型 (sqlite3 版本)
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
        print(f"Database connection error in chore model: {e}")
        raise e

def create(data):
    """
    建立新家事任務
    :param data: dict, 包含 group_id, title, description, recurrence, due_date, assigned_to, created_by
    :return: int 新增的任務 ID 或 None
    """
    sql = """
    INSERT INTO chores (group_id, title, description, recurrence, due_date, assigned_to, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('title'),
                data.get('description'),
                data.get('recurrence', 'once'),
                data.get('due_date'),
                data.get('assigned_to'),
                data.get('status', 'pending'),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create chore: {e}")
        return None

def get_all():
    """
    取得所有家事任務記錄
    :return: list of Row
    """
    sql = "SELECT * FROM chores"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all chores: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有家事任務
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM chores WHERE group_id = ? ORDER BY due_date ASC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id chores ({group_id}): {e}")
        return []

def get_pending_by_user(user_id):
    """
    取得某個使用者「所有待完成」的家事任務
    :param user_id: int, 使用者 ID
    :return: list of Row
    """
    sql = "SELECT * FROM chores WHERE assigned_to = ? AND status = 'pending' ORDER BY due_date ASC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_pending_by_user chores ({user_id}): {e}")
        return []

def get_by_id(chore_id):
    """
    依 ID 取得單筆家事任務
    :param chore_id: int, 任務 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM chores WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (chore_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id chore ({chore_id}): {e}")
        return None

def update(chore_id, data):
    """
    更新家事任務資料
    :param chore_id: int, 任務 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE chores SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(chore_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update chore ({chore_id}): {e}")
        return False

def mark_completed(chore_id):
    """
    標記家事為已完成。
    
    Args:
        chore_id (int): 家事 ID。
        
    Returns:
        bool: 是否標記成功。
    """
    sql = "UPDATE chores SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (chore_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error marking chore as completed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

    將家事任務標記為已完成，自動寫入完成時間 (completed_at)
    :param chore_id: int, 任務 ID
    :return: bool 是否成功
    """
    sql = """
    UPDATE chores
    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (chore_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in mark_completed chore ({chore_id}): {e}")
        return False

def delete(chore_id):
    """
    刪除家事任務
    :param chore_id: int, 任務 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM chores WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (chore_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete chore ({chore_id}): {e}")
        return False
