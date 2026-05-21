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
    finally:
        if conn:
            conn.close()
