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
