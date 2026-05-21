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
    新增一筆家事任務記錄
    :param data: dict, 包含 group_id, title, description, recurrence, due_date, assigned_to, status, created_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chores (group_id, title, description, recurrence, due_date, assigned_to, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('title'),
                data.get('description'),
                data.get('recurrence', 'once'),
                data.get('due_date'),
                data.get('assigned_to'),
                data.get('status', 'pending'),
                data.get('created_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in chore.create: {e}")
        raise e

def get_all():
    """
    取得所有家事任務記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM chores").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in chore.get_all: {e}")
        raise e

def get_by_id(chore_id):
    """
    根據 ID 取得單筆家事任務記錄
    :param chore_id: int, 家事 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM chores WHERE id = ?", (chore_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in chore.get_by_id: {e}")
        raise e

def update(chore_id, data):
    """
    更新家事任務記錄（如完成狀態、負責人、到期日等）
    :param chore_id: int, 家事 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'title', 'description', 'recurrence', 'due_date', 'assigned_to', 'status', 'created_by', 'completed_at']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(chore_id)
        sql = f"UPDATE chores SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in chore.update: {e}")
        raise e

def delete(chore_id):
    """
    刪除家事任務記錄
    :param chore_id: int, 家事 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM chores WHERE id = ?", (chore_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in chore.delete: {e}")
        raise e

def get_by_group(group_id):
    """
    取得特定群組的所有家事任務記錄
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM chores WHERE group_id = ? ORDER BY due_date ASC", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in chore.get_by_group: {e}")
        raise e

