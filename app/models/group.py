import sqlite3
import os

def get_db_connection():
    """建立並回傳 SQLite 資料庫連線，設定 Row factory 並啟用外鍵約束"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create(data):
    """
    新增一筆群組記錄
    :param data: dict, 包含 name, invite_code, created_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO groups (name, invite_code, created_by) VALUES (?, ?, ?)",
            (
                data.get('name'),
                data.get('invite_code'),
                data.get('created_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in group.create: {e}")
        raise e

def get_all():
    """
    取得所有群組記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM groups").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in group.get_all: {e}")
        raise e

def get_by_id(group_id):
    """
    根據 ID 取得單筆群組記錄
    :param group_id: int, 群組 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in group.get_by_id: {e}")
        raise e

def get_by_invite_code(invite_code):
    """
    根據邀請碼取得單筆群組記錄
    :param invite_code: str, 邀請碼
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM groups WHERE invite_code = ?", (invite_code,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in group.get_by_invite_code: {e}")
        raise e

def update(group_id, data):
    """
    更新群組記錄
    :param group_id: int, 群組 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['name', 'invite_code', 'created_by']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(group_id)
        sql = f"UPDATE groups SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in group.update: {e}")
        raise e

def delete(group_id):
    """
    刪除群組記錄
    :param group_id: int, 群組 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in group.delete: {e}")
        raise e
