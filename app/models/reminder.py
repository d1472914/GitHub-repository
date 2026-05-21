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
    發送一筆匿名提醒。
    注意：在發送前，Controller 應先呼叫 `get_cooldown_status` 檢查冷卻時間。
    
    Args:
        data (dict): 包含 group_id, sender_id, receiver_id, category, message 的字典。
        
    Returns:
        int: 新增提醒的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO reminders (group_id, sender_id, receiver_id, category, message)
        VALUES (?, ?, ?, ?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            data.get('group_id'),
            data.get('sender_id'),
            data.get('receiver_id'),
            data.get('category'),
            data.get('message')
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating reminder: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有提醒記錄。
    
    Returns:
        list: 所有提醒記錄列表。
    """
    sql = "SELECT * FROM reminders"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all reminders: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(reminder_id):
    """
    取得單筆提醒。
    
    Args:
        reminder_id (int): 提醒 ID。
        
    Returns:
        sqlite3.Row: 提醒記錄。
    """
    sql = "SELECT * FROM reminders WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (reminder_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting reminder by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update(reminder_id, data):
    """
    更新提醒。
    
    Args:
        reminder_id (int): 提醒 ID。
        data (dict): 更新的欄位與值。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': reminder_id}
    for key in ['category', 'message']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE reminders SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating reminder: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(reminder_id):
    """
    刪除提醒。
    
    Args:
        reminder_id (int): 提醒 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    sql = "DELETE FROM reminders WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (reminder_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting reminder: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助功能：安全匿名查詢與冷卻檢查 ---

def get_received_reminders(user_id):
    """
    安全查詢：取得特定使用者收到的提醒。
    ⚠️ 為確保匿名性，此查詢中絕對不包含 sender_id 欄位。
    
    Args:
        user_id (int): 接收提醒的使用者 ID。
        
    Returns:
        list: 收到的提醒記錄列表（只含 id, category, message, created_at）。
    """
    sql = """
        SELECT id, category, message, created_at 
        FROM reminders 
        WHERE receiver_id = ? 
        ORDER BY created_at DESC
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting received reminders for user {user_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_cooldown_status(sender_id, receiver_id):
    """
    檢查發送者在過去 1 小時內，是否已發送過提醒給同一個接收者。
    
    Args:
        sender_id (int): 發送者 ID。
        receiver_id (int): 接收者 ID。
        
    Returns:
        bool: True 表示仍在冷卻中（不能發送），False 表示冷卻已結束（可以發送）。
    """
    # 判斷一小時內有無紀錄。SQLite datetime('now', '-1 hour') 使用世界協調時間（UTC）
    # 因為 CURRENT_TIMESTAMP 在 SQLite 中是 UTC 時間，這點兩者吻合。
    sql = """
        SELECT COUNT(*) 
        FROM reminders 
        WHERE sender_id = ? AND receiver_id = ? 
          AND created_at >= datetime('now', '-1 hour')
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (sender_id, receiver_id))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        logging.error(f"Error checking reminder cooldown: {e}")
        return True # 發生錯誤時保守回傳 True (處於冷卻中)
    finally:
        if conn:
            conn.close()

def get_group_stats(group_id):
    """
    取得群組內匿名提醒的統計摘要（以分類統計次數，不洩漏個人資訊）。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        dict: 鍵為 category（如 noise, hygiene, other），值為次數的 dict。
    """
    sql = """
        SELECT category, COUNT(*) as count 
        FROM reminders 
        WHERE group_id = ? 
        GROUP BY category
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        rows = cursor.fetchall()
        
        # 初始化預設三個類別的統計
        stats = {'noise': 0, 'hygiene': 0, 'other': 0}
        for row in rows:
            cat = row['category']
            stats[cat] = row['count']
        return stats
    except sqlite3.Error as e:
        logging.error(f"Error getting group reminder stats: {e}")
        return {}
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


