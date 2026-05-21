<<<<<<< HEAD
"""
Notification Model — 站內通知 (sqlite3 版本)
儲存系統發送給使用者的通知訊息
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線並啟用外鍵"""
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
        print(f"Database connection error in notification model: {e}")
        raise e

def create(data):
    """
    建立新通知
    :param data: dict, 包含 user_id, group_id, type, title, message
    :return: int 新增的通知 ID 或 None
    """
    sql = """
    INSERT INTO notifications (user_id, group_id, type, title, message, is_read)
    VALUES (?, ?, ?, ?, ?, ?)
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                data.get('user_id'),
                data.get('group_id'),
                data.get('type'),
                data.get('title'),
                data.get('message'),
<<<<<<< HEAD
                data.get('is_read', 0)  # SQLite represents Boolean as 0 or 1
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create notification: {e}")
        return None

def get_all():
    """
    取得所有通知
    :return: list of Row 物件
    """
    sql = "SELECT * FROM notifications ORDER BY id DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all notifications: {e}")
        return []

def get_by_id(notification_id):
    """
    依 ID 取得通知
    :param notification_id: int, 通知 ID
    :return: Row 物件 或 None
    """
    sql = "SELECT * FROM notifications WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (notification_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id notification ({notification_id}): {e}")
        return None

def get_by_user(user_id):
    """
    取得某使用者的所有通知（由新到舊）
    :param user_id: int, 使用者 ID
    :return: list of Row
    """
    sql = "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_user notifications ({user_id}): {e}")
        return []

def get_unread_by_user(user_id):
    """
    取得某使用者所有未讀通知
    :param user_id: int, 使用者 ID
    :return: list of Row
    """
    sql = "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY id DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_unread_by_user notifications ({user_id}): {e}")
        return []

def get_unread_count(user_id):
    """
    取得某使用者未讀通知數量
    :param user_id: int, 使用者 ID
    :return: int 未讀數量
    """
    sql = "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0"
    try:
        with get_db_connection() as conn:
            row = conn.execute(sql, (user_id,)).fetchone()
            return row['count'] if row else 0
    except sqlite3.Error as e:
        print(f"Error in get_unread_count notifications ({user_id}): {e}")
        return 0

def mark_as_read(notification_id):
    """
    將通知標記為已讀
    :param notification_id: int, 通知 ID
    :return: bool 是否更新成功
    """
    return update(notification_id, {'is_read': 1})

def mark_all_as_read(user_id):
    """
    將某使用者所有通知標記為已讀
    :param user_id: int, 使用者 ID
    :return: bool 是否更新成功
    """
    sql = "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in mark_all_as_read notifications ({user_id}): {e}")
        return False

def update(notification_id, data):
    """
    更新通知
    :param notification_id: int, 通知 ID
    :param data: dict, 需要更新的欄位值，例如 {'is_read': 1}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE notifications SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(notification_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update notification ({notification_id}): {e}")
        return False

def delete(notification_id):
    """
    刪除通知
    :param notification_id: int, 通知 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM notifications WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (notification_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete notification ({notification_id}): {e}")
        return False
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
