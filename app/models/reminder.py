"""
Reminder Model — 匿名提醒資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error in reminder model: {e}")
        raise e

def create(data):
    """
    建立新匿名提醒記錄
    :param data: dict, 包含 group_id, sender_id, receiver_id, category, message
    :return: int 新增的提醒 ID 或 None
    """
    sql = """
    INSERT INTO reminders (group_id, sender_id, receiver_id, category, message)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
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
        print(f"Error in create reminder: {e}")
        return None

def get_all():
    """
    取得所有匿名提醒記錄
    :return: list of Row
    """
    sql = "SELECT * FROM reminders"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all reminders: {e}")
        return []

def get_inbox_by_user(user_id):
    """
    取得某人「收到」的所有匿名提醒，按發送時間排序由新到舊
    :param user_id: int, 接收者 ID
    :return: list of Row (不包含 sender_id，以維護匿名性！)
    """
    # ⚠️ 這裡在 SELECT 時刻意排除 sender_id，保證匿名性由後端強制限制！
    sql = """
    SELECT id, group_id, receiver_id, category, message, created_at
    FROM reminders
    WHERE receiver_id = ?
    ORDER BY created_at DESC
    """
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_inbox_by_user reminders ({user_id}): {e}")
        return []

def check_cooldown(sender_id, receiver_id, hours=1):
    """
    檢查發送者與接收者之間，是否仍在冷卻時間內 (1 小時內是否已發送過提醒)
    :param sender_id: int, 發送者 ID
    :param receiver_id: int, 接收者 ID
    :param hours: int, 冷卻時數，預設 1 小時
    :return: Row 或 None (如果有近期的提醒記錄)
    """
    sql = """
    SELECT * FROM reminders
    WHERE sender_id = ? AND receiver_id = ? 
      AND created_at >= datetime('now', '-' || ? || ' hour', 'localtime')
    LIMIT 1
    """
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (sender_id, receiver_id, hours)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in check_cooldown reminder: {e}")
        return None

def get_stats_by_group(group_id):
    """
    取得群組內匿名提醒的整體分類統計
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = """
    SELECT category, COUNT(*) as count
    FROM reminders
    WHERE group_id = ?
    GROUP BY category
    """
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


        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_stats_by_group reminders ({group_id}): {e}")
        return []

def get_by_id(reminder_id):
    """
    依 ID 取得單筆匿名提醒
    :param reminder_id: int, 提醒 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM reminders WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (reminder_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id reminder ({reminder_id}): {e}")
        return None

def update(reminder_id, data):
    """
    更新提醒資料
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE reminders SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(reminder_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update reminder ({reminder_id}): {e}")
        return False

def delete(reminder_id):
    """
    刪除提醒記錄
    :param reminder_id: int, 提醒 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM reminders WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (reminder_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete reminder ({reminder_id}): {e}")
        return False
