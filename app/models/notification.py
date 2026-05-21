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
    建立一筆站內通知。
    
    Args:
        data (dict): 包含 user_id, group_id, type, title, message 的字典。
        
    Returns:
        int: 新增通知的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO notifications (user_id, group_id, type, title, message, is_read)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            data.get('user_id'),
            data.get('group_id'),
            data.get('type'),
            data.get('title'),
            data.get('message'),
            data.get('is_read', 0)
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating notification: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有通知。
    
    Returns:
        list: 所有通知記錄列表。
    """
    sql = "SELECT * FROM notifications"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all notifications: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(notification_id):
    """
    取得單筆通知。
    
    Args:
        notification_id (int): 通知 ID。
        
    Returns:
        sqlite3.Row: 通知記錄。
    """
    sql = "SELECT * FROM notifications WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (notification_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting notification by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update(notification_id, data):
    """
    更新通知狀態（如標記單筆通知為已讀/未讀）。
    
    Args:
        notification_id (int): 通知 ID。
        data (dict): 更新的欄位與值（如 is_read）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': notification_id}
    for key in ['is_read', 'title', 'message']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE notifications SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating notification: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(notification_id):
    """
    刪除通知。
    
    Args:
        notification_id (int): 通知 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    sql = "DELETE FROM notifications WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (notification_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting notification: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助功能：未讀通知查詢與批次已讀 ---

def get_unread_notifications(user_id):
    """
    取得特定使用者未讀的站內通知。
    
    Args:
        user_id (int): 使用者 ID。
        
    Returns:
        list: 未讀通知記錄列表。
    """
    sql = "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting unread notifications: {e}")
        return []
    finally:
        if conn:
            conn.close()

def mark_all_read(user_id):
    """
    將使用者的所有未讀通知標記為已讀。
    
    Args:
        user_id (int): 使用者 ID。
        
    Returns:
        bool: 是否標記成功。
    """
    sql = "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        conn.commit()
        return True # 不論原本有沒有未讀通知，只要執行成功都算成功
    except sqlite3.Error as e:
        logging.error(f"Error marking all notifications as read: {e}")
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
    新增一筆站內通知記錄
    :param data: dict, 包含 user_id, group_id, type, title, message, is_read
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notifications (user_id, group_id, type, title, message, is_read) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data.get('user_id'),
                data.get('group_id'),
                data.get('type'),
                data.get('title'),
                data.get('message'),
                data.get('is_read', 0)
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in notification.create: {e}")
        raise e

def get_all():
    """
    取得所有站內通知記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM notifications").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in notification.get_all: {e}")
        raise e

def get_by_id(notification_id):
    """
    根據 ID 取得單筆站內通知記錄
    :param notification_id: int, 通知 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in notification.get_by_id: {e}")
        raise e

def get_unread_by_user(user_id):
    """
    取得某使用者的所有未讀站內通知
    :param user_id: int, 使用者 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in notification.get_unread_by_user: {e}")
        raise e

def update(notification_id, data):
    """
    更新站內通知記錄（如標記為已讀）
    :param notification_id: int, 通知 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['user_id', 'group_id', 'type', 'title', 'message', 'is_read']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(notification_id)
        sql = f"UPDATE notifications SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in notification.update: {e}")
        raise e

def delete(notification_id):
    """
    刪除站內通知記錄
    :param notification_id: int, 通知 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in notification.delete: {e}")
        raise e
