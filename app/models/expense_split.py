"""
ExpenseSplit Model — 開支分攤資料模型 (sqlite3 版本)
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
        print(f"Database connection error in expense_split model: {e}")
        raise e

def create(data):
    """
    建立新開支分攤記錄
    :param data: dict, 包含 expense_id, user_id, amount, is_settled
    :return: int 新增的分攤記錄 ID 或 None
    """
    sql = """
    INSERT INTO expense_splits (expense_id, user_id, amount, is_settled)
    VALUES (?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('expense_id'),
                data.get('user_id'),
                data.get('amount'),
                data.get('is_settled', 0)
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create expense_split: {e}")
        return None

def get_all():
    """
    取得所有分攤記錄
    :return: list of Row
    """
    sql = "SELECT * FROM expense_splits"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all expense_splits: {e}")
        return []

def get_by_expense_id(expense_id):
    """
    取得某一筆開支的所有分攤明細
    :param expense_id: int, 開支 ID
    :return: list of Row
    """
    sql = "SELECT * FROM expense_splits WHERE expense_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (expense_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_expense_id splits ({expense_id}): {e}")
        return []

def get_by_id(split_id):
    """
    依 ID 取得單筆分攤記錄
    :param split_id: int, 分攤記錄 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM expense_splits WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (split_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id expense_split ({split_id}): {e}")
        return None

def get_unsettled_by_user(user_id):
    """
    取得某個使用者所有「未結清」的應付分攤記錄
    :param user_id: int, 使用者 ID
    :return: list of Row
    """
    sql = """
    SELECT es.*, e.title, e.amount as total_amount, e.paid_by, e.created_at
    FROM expense_splits es
    JOIN expenses e ON es.expense_id = e.id
    WHERE es.user_id = ? AND es.is_settled = 0
    """
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_unsettled_by_user splits ({user_id}): {e}")
        return []

def mark_settled_between_users(user1_id, user2_id):
    """
    將兩位使用者之間「所有未結清」的帳務標記為已結清
    :param user1_id: int, 使用者 1 ID
    :param user2_id: int, 使用者 2 ID
    :return: bool 是否操作成功
    """
    # 狀況 1：user1 幫忙付，user2 應付的分攤
    sql1 = """
    UPDATE expense_splits
    SET is_settled = 1
    WHERE user_id = ? AND is_settled = 0 AND expense_id IN (
        SELECT id FROM expenses WHERE paid_by = ?
    )
    """
    # 狀況 2：user2 幫忙付，user1 應付的分攤
    sql2 = """
    UPDATE expense_splits
    SET is_settled = 1
    WHERE user_id = ? AND is_settled = 0 AND expense_id IN (
        SELECT id FROM expenses WHERE paid_by = ?
    )
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql1, (user2_id, user1_id))
            cursor.execute(sql2, (user1_id, user2_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error in mark_settled_between_users ({user1_id} - {user2_id}): {e}")
        return False

def update(split_id, data):
    """
    更新分攤資料
    :param split_id: int, 分攤 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE expense_splits SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(split_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update expense_split ({split_id}): {e}")
        return False

def delete(split_id):
    """
    刪除分攤記錄
    :param split_id: int, 分攤 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM expense_splits WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (split_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete expense_split ({split_id}): {e}")
        return False
