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
