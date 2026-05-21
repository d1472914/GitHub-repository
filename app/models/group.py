import sqlite3
import os
import logging

def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線。
    資料庫路徑為 instance/database.db，並啟用外鍵約束與 Row factory。
    
    Returns:
        sqlite3.Connection: 資料庫連線物件
    """
    try:
        db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

def create(data):
    """
    建立一個新的群組。
    
    Args:
        data (dict): 包含 name, invite_code, created_by 的字典。
        
    Returns:
        int: 新增群組的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO groups (name, invite_code, created_by)
        VALUES (:name, :invite_code, :created_by)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = {
            'name': data.get('name'),
            'invite_code': data.get('invite_code'),
            'created_by': data.get('created_by')
        }
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating group: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有群組。
    
    Returns:
        list: 包含所有群組 sqlite3.Row 的列表。
    """
    sql = "SELECT * FROM groups"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all groups: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(group_id):
    """
    取得單筆群組記錄。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        sqlite3.Row: 群組記錄，若不存在或失敗則回傳 None。
    """
    sql = "SELECT * FROM groups WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting group by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_invite_code(invite_code):
    """
    依邀請碼取得單筆群組記錄（用於加入群組）。
    
    Args:
        invite_code (str): 群組邀請碼。
        
    Returns:
        sqlite3.Row: 群組記錄，若不存在或失敗則回傳 None。
    """
    sql = "SELECT * FROM groups WHERE invite_code = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (invite_code,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting group by invite_code: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update(group_id, data):
    """
    更新群組資料。
    
    Args:
        group_id (int): 群組 ID。
        data (dict): 需要更新的欄位與值的字典（如 name, invite_code, created_by）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': group_id}
    for key in ['name', 'invite_code', 'created_by']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE groups SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating group: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(group_id):
    """
    刪除群組。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    sql = "DELETE FROM groups WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting group: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

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
