"""
AgreementVersion Model — 公約版本歷史資料模型 (sqlite3 版本)
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
        print(f"Database connection error in agreement_version model: {e}")
        raise e

def create(data):
    """
    建立新公約版本歷史記錄
    :param data: dict, 包含 agreement_id, version_number, content_before, content_after, modified_by
    :return: int 新增的版本記錄 ID 或 None
    """
    sql = """
    INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('agreement_id'),
                data.get('version_number'),
                data.get('content_before'),
                data.get('content_after'),
                data.get('modified_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create agreement_version: {e}")
        return None

def get_all():
    """
    取得所有版本歷史記錄
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_versions"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all agreement_versions: {e}")
        return []

def get_by_agreement_id(agreement_id):
    """
    取得某公約的所有版本歷史，依版本號由大到小排序
    :param agreement_id: int, 公約 ID
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_versions WHERE agreement_id = ? ORDER BY version_number DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_agreement_id versions ({agreement_id}): {e}")
        return []

def get_by_id(version_id):
    """
    依 ID 取得單筆版本記錄
    :param version_id: int, 版本記錄 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreement_versions WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (version_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id agreement_version ({version_id}): {e}")
        return None

def update(version_id, data):
    """
    更新版本記錄 (通常歷史記錄不常修改)
    :param version_id: int, 版本記錄 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE agreement_versions SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(version_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update agreement_version ({version_id}): {e}")
        return False

def delete(version_id):
    """
    刪除版本記錄
    :param version_id: int, 版本記錄 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM agreement_versions WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (version_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete agreement_version ({version_id}): {e}")
        return False
