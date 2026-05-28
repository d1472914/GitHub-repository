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
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
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
                data.get('user_id'),
                data.get('group_id'),
                data.get('type'),
                data.get('title'),
                data.get('message'),
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
