<<<<<<< HEAD
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
        db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
<<<<<<< HEAD
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
=======
        logging.error(f"Database connection error: {e}")
        raise

def create(data):
    """
    建立一個家事任務。
    
    Args:
        data (dict): 包含 group_id, title, description, recurrence, due_date, assigned_to, created_by 的字典。
        
    Returns:
        int: 新增任務的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO chores (group_id, title, description, recurrence, due_date, assigned_to, created_by, status)
        VALUES (:group_id, :title, :description, :recurrence, :due_date, :assigned_to, :created_by, :status)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = {
            'group_id': data.get('group_id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'recurrence': data.get('recurrence', 'once'),
            'due_date': data.get('due_date'),
            'assigned_to': data.get('assigned_to'),
            'created_by': data.get('created_by'),
            'status': data.get('status', 'pending')
        }
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating chore: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有家事任務。
    
    Returns:
        list: 所有家事記錄列表。
    """
    sql = "SELECT * FROM chores"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all chores: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(chore_id):
    """
    取得單筆家事任務。
    
    Args:
        chore_id (int): 家事 ID。
        
    Returns:
        sqlite3.Row: 家事記錄。
    """
    sql = "SELECT * FROM chores WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (chore_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting chore by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_group(group_id):
    """
    取得群組的所有家事任務，包含負責人暱稱。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 家事記錄列表。
    """
    sql = """
        SELECT c.*, u.nickname as assigned_to_name 
        FROM chores c
        JOIN users u ON c.assigned_to = u.id
        WHERE c.group_id = ?
        ORDER BY c.due_date ASC
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting chores by group: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_user(user_id):
    """
    取得個人的待辦家事任務（狀態為 pending）。
    
    Args:
        user_id (int): 使用者 ID。
        
    Returns:
        list: 個人待辦家事記錄列表。
    """
    sql = "SELECT * FROM chores WHERE assigned_to = ? AND status = 'pending' ORDER BY due_date ASC"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting chores by user: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update(chore_id, data):
    """
    更新家事任務內容。
    
    Args:
        chore_id (int): 家事 ID。
        data (dict): 更新的欄位與值（如 title, description, recurrence, due_date, assigned_to, status）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': chore_id}
    
    # 支持更新的欄位
    for key in ['title', 'description', 'recurrence', 'due_date', 'assigned_to', 'status']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    # 如果更新狀態為 completed，則自動設定 completed_at = CURRENT_TIMESTAMP
    if data.get('status') == 'completed':
        fields.append("completed_at = CURRENT_TIMESTAMP")
    elif data.get('status') == 'pending':
        fields.append("completed_at = NULL")
        
    if not fields:
        return False
        
    sql = f"UPDATE chores SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating chore: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(chore_id):
    """
    刪除家事任務。
    
    Args:
        chore_id (int): 家事 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    sql = "DELETE FROM chores WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (chore_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting chore: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                data.get('group_id'),
                data.get('title'),
                data.get('description'),
                data.get('recurrence', 'once'),
                data.get('due_date'),
                data.get('assigned_to'),
                data.get('status', 'pending'),
                data.get('created_by')
<<<<<<< HEAD
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create chore: {e}")
        return None
=======
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in chore.create: {e}")
        raise e
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

def get_all():
    """
    取得所有家事任務記錄
<<<<<<< HEAD
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
=======
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

>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
