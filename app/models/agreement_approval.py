"""
AgreementApproval Model — 公約同意記錄資料模型 (sqlite3 版本)
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
        print(f"Database connection error in agreement_approval model: {e}")
        raise e

def create(data):
    """
    建立新同意記錄
    :param data: dict, 包含 agreement_id, user_id
    :return: int 新增的記錄 ID 或 None
    """
    sql = """
    INSERT INTO agreement_approvals (agreement_id, user_id)
    VALUES (?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('agreement_id'),
                data.get('user_id')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        # 如果因為 UNIQUE 約束報錯，表示已同意過
        print(f"Error in create agreement_approval: {e}")
        return None

def get_all():
    """
    取得所有同意記錄
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_approvals"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all agreement_approvals: {e}")
        return []

def get_by_agreement_id(agreement_id):
    """
    取得某公約的所有同意記錄
    :param agreement_id: int, 公約 ID
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_approvals WHERE agreement_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_agreement_id approvals ({agreement_id}): {e}")
        return []

def get_by_id(approval_id):
    """
    依 ID 取得單筆同意記錄
    :param approval_id: int, 同意記錄 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreement_approvals WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (approval_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id agreement_approval ({approval_id}): {e}")
        return None

def check_exists(agreement_id, user_id):
    """
    檢查某個使用者是否已同意過某公約
    :param agreement_id: int, 公約 ID
    :param user_id: int, 使用者 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreement_approvals WHERE agreement_id = ? AND user_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id, user_id)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in check_exists agreement_approval: {e}")
        return None

def delete_by_agreement_id(agreement_id):
    """
    刪除某公約的所有同意記錄 (當公約內容修改時需要重設)
    :param agreement_id: int, 公約 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM agreement_approvals WHERE agreement_id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (agreement_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete_by_agreement_id approvals ({agreement_id}): {e}")
        return False

def update(approval_id, data):
    """
    更新同意記錄 (通常很少使用)
    """
    if not data:
        return False
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE agreement_approvals SET {set_clause} WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(approval_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update agreement_approval ({approval_id}): {e}")
        return False

def delete(approval_id):
    """
    刪除單筆同意記錄
    """
    sql = "DELETE FROM agreement_approvals WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (approval_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete agreement_approval ({approval_id}): {e}")
        return False
