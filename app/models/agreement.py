"""
Agreement Model — 公約資料模型 (sqlite3 版本)
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
        print(f"Database connection error in agreement model: {e}")
        raise e

def create(data):
    """
    建立新公約記錄
    :param data: dict, 包含 group_id, title, category, content, status, created_by
    :return: int 新增的公約 ID 或 None
    """
    sql = """
    INSERT INTO agreements (group_id, title, category, content, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('title'),
                data.get('category'),
                data.get('content'),
                data.get('status', 'pending'),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create agreement: {e}")
        return None

def get_all():
    """
    取得所有公約記錄
    :return: list of Row
    """
    sql = "SELECT * FROM agreements"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all agreements: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有公約記錄
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM agreements WHERE group_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id agreements ({group_id}): {e}")
        return []

def get_by_id(agreement_id):
    """
    依 ID 取得單筆公約記錄
    :param agreement_id: int, 公約 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreements WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id agreement ({agreement_id}): {e}")
        return None

def update(agreement_id, data):
    """
    更新公約資料
    :param agreement_id: int, 公約 ID
    :param data: dict, 需要更新的欄位值，例如 {'title': '新公約名稱', 'content': '新內容', 'status': 'active', 'updated_at': '...'}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    # 自動補上更新時間欄位，若沒有帶的話
    if 'updated_at' not in keys:
        keys.append('updated_at')
        data['updated_at'] = sqlite3.Timestamp if hasattr(sqlite3, 'Timestamp') else 'CURRENT_TIMESTAMP'
        # 由於 CURRENT_TIMESTAMP 在預留字元中會作為字串寫入，這裡我們用 SQLite 內置函數在組裝時特別處理
        
    set_clauses = []
    params = []
    for key in keys:
        if key == 'updated_at' and data[key] == 'CURRENT_TIMESTAMP':
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        else:
            set_clauses.append(f"{key} = ?")
            params.append(data[key])
            
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE agreements SET {set_clause} WHERE id = ?"
    params.append(agreement_id)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update agreement ({agreement_id}): {e}")
        return False

def delete(agreement_id):
    """
    刪除公約記錄
    :param agreement_id: int, 公約 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM agreements WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (agreement_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete agreement ({agreement_id}): {e}")
        return False
