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
                data.get('email'),
                data.get('password_hash'),
                data.get('nickname'),
                data.get('role', 'member'),
                data.get('group_id')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in user.create: {e}")
        raise e

def get_all():
    """
    取得所有使用者記錄
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

def delete(user_id):
    """
    刪除使用者記錄
    :param user_id: int, 使用者 ID
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

