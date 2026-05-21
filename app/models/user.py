<<<<<<< HEAD
"""
User Model — 使用者資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """
    建立 SQLite 資料庫連線，並設定 row_factory 為 Row。
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
<<<<<<< HEAD
        print(f"Database connection error in user model: {e}")
        raise e

def create(data):
    """
    建立新使用者記錄
    :param data: dict, 包含 email, password_hash, nickname, role, group_id
    :return: int 新增的使用者 ID 或 None
    """
    sql = """
    INSERT INTO users (email, password_hash, nickname, role, group_id)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
=======
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
    新增一筆使用者記錄
    :param data: dict, 包含 email, password_hash, nickname, role, group_id
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, nickname, role, group_id) VALUES (?, ?, ?, ?, ?)",
            (
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                data.get('email'),
                data.get('password_hash'),
                data.get('nickname'),
                data.get('role', 'member'),
                data.get('group_id')
<<<<<<< HEAD
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create user: {e}")
        return None
=======
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in user.create: {e}")
        raise e
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

def get_all():
    """
    取得所有使用者記錄
<<<<<<< HEAD
    :return: list of Row 物件
    """
    sql = "SELECT * FROM users"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all users: {e}")
        return []

def get_by_id(user_id):
    """
    依 ID 取得單筆使用者記錄
    :param user_id: int, 使用者 ID
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM users WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id user ({user_id}): {e}")
        return None

def get_by_email(email):
    """
    依 Email 取得單筆使用者記錄 (供認證路由使用)
    :param email: str, 使用者信箱
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM users WHERE email = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (email,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_email user ({email}): {e}")
        return None

def get_by_group_id(group_id):
    """
    依群組 ID 取得該群組內的所有使用者
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM users WHERE group_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id users ({group_id}): {e}")
        return []

def update(user_id, data):
    """
    更新使用者資料
    :param user_id: int, 使用者 ID
    :param data: dict, 需要更新的欄位值，例如 {'nickname': '新暱稱', 'group_id': 2}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE users SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(user_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update user ({user_id}): {e}")
        return False
=======
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in user.get_all: {e}")
        raise e

def get_by_id(user_id):
    """
    根據 ID 取得單筆使用者記錄
    :param user_id: int, 使用者 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in user.get_by_id: {e}")
        raise e

def get_by_email(email):
    """
    根據 Email 取得單筆使用者記錄（常供登入使用）
    :param email: str, 使用者 Email
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in user.get_by_email: {e}")
        raise e

def update(user_id, data):
    """
    更新使用者記錄
    :param user_id: int, 使用者 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['email', 'password_hash', 'nickname', 'role', 'group_id']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in user.update: {e}")
        raise e
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

def delete(user_id):
    """
    刪除使用者記錄
    :param user_id: int, 使用者 ID
<<<<<<< HEAD
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM users WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete user ({user_id}): {e}")
        return False
=======
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in user.delete: {e}")
        raise e

def get_users_by_group(group_id):
    """
    取得該群組內的所有使用者
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users WHERE group_id = ?", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in user.get_users_by_group: {e}")
        raise e

>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
