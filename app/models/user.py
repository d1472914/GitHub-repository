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
        # 資料庫檔案路徑設在根目錄的 instance/database.db
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
    新增一筆使用者記錄。
    
    Args:
        data (dict): 包含 email, password_hash, nickname, role, group_id 的字典。
        
    Returns:
        int: 新增記錄的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO users (email, password_hash, nickname, role, group_id)
        VALUES (:email, :password_hash, :nickname, :role, :group_id)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 設定預設 role
        params = {
            'email': data.get('email'),
            'password_hash': data.get('password_hash'),
            'nickname': data.get('nickname'),
            'role': data.get('role', 'member'),
            'group_id': data.get('group_id')
        }
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating user: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有使用者記錄。
    
    Returns:
        list: 包含所有使用者 sqlite3.Row 的列表，失敗則回傳空列表。
    """
    sql = "SELECT * FROM users"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all users: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(user_id):
    """
    取得單筆使用者記錄。
    
    Args:
        user_id (int): 使用者 ID。
        
    Returns:
        sqlite3.Row: 使用者記錄，若不存在或失敗則回傳 None。
    """
    sql = "SELECT * FROM users WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting user by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_email(email):
    """
    依 email 取得單筆使用者記錄（用於登入驗證）。
    
    Args:
        email (str): 使用者信箱。
        
    Returns:
        sqlite3.Row: 使用者記錄，若不存在或失敗則回傳 None。
    """
    sql = "SELECT * FROM users WHERE email = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (email,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting user by email: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update(user_id, data):
    """
    更新使用者記錄。只更新傳入的欄位。
    
    Args:
        user_id (int): 使用者 ID。
        data (dict): 需要更新的欄位與值的字典（如 email, nickname, password_hash, role, group_id）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    # 動態組合 SQL
    fields = []
    params = {'id': user_id}
    for key in ['email', 'password_hash', 'nickname', 'role', 'group_id']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE users SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(user_id):
    """
    刪除使用者記錄。
    
    Args:
        user_id (int): 使用者 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    sql = "DELETE FROM users WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_users_by_group(group_id):
    """
    取得該群組內的所有使用者。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 使用者記錄列表。
    """
    sql = "SELECT * FROM users WHERE group_id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting users by group: {e}")
        return []
    finally:
        if conn:
            conn.close()

