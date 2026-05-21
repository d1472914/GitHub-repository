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
    新增一筆匿名提醒記錄
    :param data: dict, 包含 group_id, sender_id, receiver_id, category, message
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (group_id, sender_id, receiver_id, category, message) VALUES (?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('sender_id'),
                data.get('receiver_id'),
                data.get('category'),
                data.get('message')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in reminder.create: {e}")
        raise e

def get_all():
    """
    取得所有匿名提醒記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM reminders").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_all: {e}")
        raise e

def get_by_id(reminder_id):
    """
    根據 ID 取得單筆匿名提醒記錄
    :param reminder_id: int, 提醒 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_by_id: {e}")
        raise e

def get_recent_reminders(sender_id, receiver_id, limit_hours=1):
    """
    取得某發送者發送給某接收者的最近提醒（常用於冷卻機制檢查）
    :param sender_id: int, 發送者 ID
    :param receiver_id: int, 接收者 ID
    :param limit_hours: int, 限制小時數（預設 1 小時）
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        # SQLite 判斷時間間隔：strftime('%s', 'now') - strftime('%s', created_at)
        sql = """
            SELECT * FROM reminders
            WHERE sender_id = ? AND receiver_id = ?
            AND (strftime('%s', 'now') - strftime('%s', created_at)) < ?
        """
        rows = conn.execute(sql, (sender_id, receiver_id, limit_hours * 3600)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_recent_reminders: {e}")
        raise e

def update(reminder_id, data):
    """
    更新匿名提醒記錄
    :param reminder_id: int, 提醒 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'sender_id', 'receiver_id', 'category', 'message']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(reminder_id)
        sql = f"UPDATE reminders SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in reminder.update: {e}")
        raise e

def delete(reminder_id):
    """
    刪除匿名提醒記錄
    :param reminder_id: int, 提醒 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in reminder.delete: {e}")
        raise e

def get_stats_by_group(group_id):
    """
    依類別統計某群組的提醒次數
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row, contains 'category' and 'count'
    """
    try:
        conn = get_db_connection()
        sql = """
            SELECT category, COUNT(*) as count
            FROM reminders
            WHERE group_id = ?
            GROUP BY category
        """
        rows = conn.execute(sql, (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_stats_by_group: {e}")
        raise e

def get_by_receiver(receiver_id):
    """
    取得某接收者的所有匿名提醒記錄
    :param receiver_id: int, 接收者 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM reminders WHERE receiver_id = ? ORDER BY created_at DESC", (receiver_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in reminder.get_by_receiver: {e}")
        raise e


